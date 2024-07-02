#pragma once

#include "Type.h"

class DetectStrategy {
public:
    DetectStrategy() {};
    virtual ~DetectStrategy() {};

    virtual void detect(const cv::Mat& Frame) = 0;
    virtual void sync(TDetected (&detected)[], int &numDetected) = 0;
    virtual int getType() = 0;
};
