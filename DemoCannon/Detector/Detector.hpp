#pragma once

#include "Type.h"
#include "DetectStrategy.hpp"

class Detector {
public:
    Detector(DetectStrategy *strategy);
    ~Detector();

    void detect(const cv::Mat& Frame);
    void draw(const cv::Mat& Frame);
    TDetected getDetectedItem(int target);
    void setStrategy(DetectStrategy *strategy);

private:
    TDetected detected[20];
    int numDetected;
    DetectStrategy *strategy;
    pthread_mutexattr_t MutexAttr;
    pthread_mutex_t Mutex;
};
