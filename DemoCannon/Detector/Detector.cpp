#include "Detector.hpp"

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/features2d/features2d.hpp>
#include <opencv2/features2d.hpp>
#include "opencv2/video/tracking.hpp"
#include "opencv2/imgproc/imgproc.hpp"

Detector::Detector(DetectStrategy *strategy){
    pthread_mutexattr_init(&MutexAttr);
    pthread_mutexattr_settype(&MutexAttr, PTHREAD_MUTEX_RECURSIVE);
    pthread_mutex_init(&Mutex, &MutexAttr);

    this->strategy = strategy;
    numDetected = 0;
};

Detector::~Detector() {
    delete this->strategy;
};

void Detector::detect(const cv::Mat& Frame) {
    strategy->detect(Frame);
    pthread_mutex_lock(&Mutex);
    strategy->sync(detected, numDetected);
    pthread_mutex_unlock(&Mutex);
};

void Detector::draw(const cv::Mat& Frame) {
    pthread_mutex_lock(&Mutex);
    for (int i = 0; i < numDetected; ++i)
    {
        int match = detected[i].match;
        int xmin = (int)detected[i].xmin;
        int xmax = (int)detected[i].xmax;
        int ymin = (int)detected[i].ymin;
        int ymax = (int)detected[i].ymax;
        int baseline = 0;

        cv::rectangle(Frame, cv::Point(xmin, ymin), cv::Point(xmax, ymax), cv::Scalar(10, 255, 0), 2);
        cv::String label = detected[i].label;

        cv::Size labelSize = cv::getTextSize(label, cv::FONT_HERSHEY_SIMPLEX, 0.7, 2, &baseline); // Get font size
        int label_ymin = (std::max)((int)ymin, (int)(labelSize.height + 10)); // Make sure not to draw label too close to top of window
        rectangle(Frame, cv::Point(xmin, label_ymin - labelSize.height - 10), cv::Point(xmin + labelSize.width, label_ymin + baseline - 10), cv::Scalar(255, 255, 255), cv::FILLED); // Draw white box to put label text in
        putText(Frame, label, cv::Point(xmin, label_ymin - 7), cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 0, 0), 2); // Draw label text
    }
    pthread_mutex_unlock(&Mutex);
};

TDetected Detector::getDetectedItem(int target) {
    TDetected ret;
    ret.match = -1;

    pthread_mutex_lock(&Mutex);
    for (int i = 0; i < numDetected; ++i) {
        if (detected[i].match == target) {
            ret = detected[i];
            break;
        }
    }
    pthread_mutex_unlock(&Mutex);
    return ret;
}

void Detector::setStrategy(DetectStrategy *strategy) {
    pthread_mutex_lock(&Mutex);
    delete this->strategy;
    this->strategy = strategy;
    pthread_mutex_unlock(&Mutex);
}
