#include "ObjectDetector.h"
#include <opencv2/imgproc.hpp>
#include <algorithm>

using namespace cv;

ObjectDetector::ObjectDetector(const char* tfliteModelPath, bool quantized, bool useXnn) {
    m_modelQuantized = quantized;
    initDetectionModel(tfliteModelPath, useXnn);
}

ObjectDetector::~ObjectDetector() {
    if (m_model != nullptr)
        TfLiteModelDelete(m_model);
}

void ObjectDetector::initDetectionModel(const char* tfliteModelPath, bool useXnn) {
    m_model = TfLiteModelCreateFromFile(tfliteModelPath);
    if (m_model == nullptr) {
        printf("Failed to load model");
        return;
    }

    // Build the interpreter
    TfLiteInterpreterOptions* options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreterOptionsSetNumThreads(options, 4);

    if (useXnn) {
        TfLiteXNNPackDelegateOptions xnnOpts = TfLiteXNNPackDelegateOptionsDefault();
        m_xnnpack_delegate = TfLiteXNNPackDelegateCreate(&xnnOpts);
        TfLiteInterpreterOptionsAddDelegate(options, m_xnnpack_delegate);
    }

    // Create the interpreter.
    m_interpreter = TfLiteInterpreterCreate(m_model, options);
    if (m_interpreter == nullptr) {
        printf("Failed to create interpreter");
        return;
    }

    // Allocate tensor buffers.
    if (TfLiteInterpreterAllocateTensors(m_interpreter) != kTfLiteOk) {
        printf("Failed to allocate tensors!");
        return;
    }

    // Find input tensors.
    if (TfLiteInterpreterGetInputTensorCount(m_interpreter) != 1) {
        printf("Detection model graph needs to have 1 and only 1 input!");
        return;
    }

    m_input_tensor = TfLiteInterpreterGetInputTensor(m_interpreter, 0);
    if (m_modelQuantized && m_input_tensor->type != kTfLiteUInt8) {
        printf("Detection model input should be kTfLiteUInt8!");
        return;
    }

    if (!m_modelQuantized && m_input_tensor->type != kTfLiteFloat32) {
        printf("Detection model input should be kTfLiteFloat32!");
        return;
    }
    
    if (m_input_tensor->dims->data[0] != 1) {
        printf("Detection model error\n");
        return;
    }

    model_resize_height = m_input_tensor->dims->data[1];
    model_resize_width = m_input_tensor->dims->data[2];
    model_resize_channels = m_input_tensor->dims->data[3];

    // Find output tensors.
    if (TfLiteInterpreterGetOutputTensorCount(m_interpreter) != 4) {
        printf("Detection model graph needs to have 4 and only 4 outputs!");
        return;
    }

    const char* OutputName = TfLiteTensorName(TfLiteInterpreterGetOutputTensor(m_interpreter, 0));

    if (strcmp(OutputName, "StatefulPartitionedCall:1") == 0) {
        m_output_locations = TfLiteInterpreterGetOutputTensor(m_interpreter, 1);
        m_output_classes = TfLiteInterpreterGetOutputTensor(m_interpreter, 3);
        m_output_scores = TfLiteInterpreterGetOutputTensor(m_interpreter, 0);
        m_num_detections = TfLiteInterpreterGetOutputTensor(m_interpreter, 2);
    } else {
        m_output_locations = TfLiteInterpreterGetOutputTensor(m_interpreter, 0);
        m_output_classes = TfLiteInterpreterGetOutputTensor(m_interpreter, 1);
        m_output_scores = TfLiteInterpreterGetOutputTensor(m_interpreter, 2);
        m_num_detections = TfLiteInterpreterGetOutputTensor(m_interpreter, 3);
    }
}

float ObjectDetector::intersectionOverUnion(const DetectResult& a, const DetectResult& b) {
    float intersectionXMin = std::max(a.xmin, b.xmin);
    float intersectionYMin = std::max(a.ymin, b.ymin);
    float intersectionXMax = std::min(a.xmax, b.xmax);
    float intersectionYMax = std::min(a.ymax, b.ymax);

    float intersectionArea = std::max(0.0f, intersectionXMax - intersectionXMin) *
                             std::max(0.0f, intersectionYMax - intersectionYMin);

    float boxAArea = (a.xmax - a.xmin) * (a.ymax - a.ymin);
    float boxBArea = (b.xmax - b.xmin) * (b.ymax - b.ymin);

    float unionArea = boxAArea + boxBArea - intersectionArea;

	// printf("[SIMSON] In intersectionOverUnion value is (%f)\n", intersectionArea / unionArea);

    return intersectionArea / unionArea;
}

std::vector<int> ObjectDetector::applyNMS(const std::vector<DetectResult>& detections, float iouThreshold) {
    std::vector<int> indices;
    std::vector<bool> suppressed(detections.size(), false);

    for (size_t i = 0; i < detections.size(); ++i) {
        if (suppressed[i])
            continue;

        indices.push_back(i);

        for (size_t j = i + 1; j < detections.size(); ++j) {
            if (intersectionOverUnion(detections[i], detections[j]) > iouThreshold) {
				// printf("[SIMSON]In applyNMS, Suppressed, label(%d)\n", detections[j].label);
                suppressed[j] = true;
            }
        }
    }

    return indices;
}

DetectResult* ObjectDetector::detect(Mat src) {
    DetectResult* res = new DetectResult[DETECT_NUM];
    if (m_model == nullptr) {
        return res;
    }

    Mat image;
    resize(src, image, Size(model_resize_width, model_resize_height), 0, 0, INTER_AREA);
    int cnls = image.type();
    if (cnls == CV_8UC1) {
        cvtColor(image, image, COLOR_GRAY2RGB);
    } else if (cnls == CV_8UC3) {
        cvtColor(image, image, COLOR_BGR2RGB);
    } else if (cnls == CV_8UC4) {
        cvtColor(image, image, COLOR_BGRA2RGB);
    }

    if (m_modelQuantized) {
        uchar* dst = m_input_tensor->data.uint8;
        memcpy(dst, image.data,
            sizeof(uchar) * model_resize_width * model_resize_height * model_resize_channels);
    } else {
        Mat fimage;
        image.convertTo(fimage, CV_32FC3, 1 / IMAGE_STD, -IMAGE_MEAN / IMAGE_STD);

        float* dst = m_input_tensor->data.f;
        memcpy(dst, fimage.data,
            sizeof(float) * model_resize_width * model_resize_height * model_resize_channels);
    }

    if (TfLiteInterpreterInvoke(m_interpreter) != kTfLiteOk) {
        printf("Error invoking detection model");
        return res;
    }

    const float* detection_locations = m_output_locations->data.f;
    const float* detection_classes = m_output_classes->data.f;
    const float* detection_scores = m_output_scores->data.f;
    const int num_detections = (int)*m_num_detections->data.f;

    std::vector<DetectResult> detections;
    for (int i = 0; i < num_detections && i < DETECT_NUM; ++i) {
        DetectResult dr;
        dr.score = detection_scores[i];
        dr.label = (int)detection_classes[i];
        dr.ymin = std::fmax(0.0f, detection_locations[4 * i] * src.rows);
        dr.xmin = std::fmax(0.0f, detection_locations[4 * i + 1] * src.cols);
        dr.ymax = std::fmin(float(src.rows - 1), detection_locations[4 * i + 2] * src.rows);
        dr.xmax = std::fmin(float(src.cols - 1), detection_locations[4 * i + 3] * src.cols);
        detections.push_back(dr);
    }

    std::vector<int> nmsIndices = applyNMS(detections, NMS_IOU_THRESHOLD);

    for (size_t i = 0; i < nmsIndices.size(); ++i) {
        res[i] = detections[nmsIndices[i]];
    }

    return res;
}
