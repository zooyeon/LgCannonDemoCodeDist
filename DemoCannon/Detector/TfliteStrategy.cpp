#include "TfliteStrategy.hpp"

TfliteStrategy::TfliteStrategy(){
    printf("TensorFlow Lite Mode\n");
    tf = new ObjectDetector("../TfLite-2.17/Data/detect.tflite", false, true);
};

TfliteStrategy::~TfliteStrategy() {
    delete tf;
    if (res != nullptr) delete[] res;
};

void TfliteStrategy::detect(const cv::Mat& Frame) {
    res = tf->detect(Frame);
};

void TfliteStrategy::sync(TDetected (&detected)[], int &numDetected) {
    numDetected = 0;
    for (int i = 0; i < tf->DETECT_NUM; ++i) 
    {
        if (res[i].score<0.30) continue;

        float x = res[i].xmin + res[i].xmax;
        float y = res[i].ymin + res[i].ymax;
        Point2f center(y / 2, x / 2);

        detected[numDetected].center = center;
        detected[numDetected].match = res[i].label;
        detected[numDetected].xmin = res[i].xmin;
        detected[numDetected].xmax = res[i].xmax;
        detected[numDetected].ymin = res[i].ymin;
        detected[numDetected].ymax = res[i].ymax;
        detected[numDetected].label = std::to_string(res[i].label) + ": " + std::to_string(int(res[i].score*100))+ "%";

        ++numDetected;
    }

    delete[] res;
    res = nullptr;
};
