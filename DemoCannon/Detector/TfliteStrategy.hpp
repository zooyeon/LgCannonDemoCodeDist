#ifndef TFLITESTRATEGY
#define TFLITESTRATEGY

#include "DetectStrategy.hpp"
#include "ObjectDetector.h"

class TfliteStrategy : public DetectStrategy {
public:
    TfliteStrategy();
    virtual ~TfliteStrategy();

    virtual void detect(const cv::Mat& Frame);
    virtual void sync(TDetected (&detected)[], int &numDetected);
    virtual int getType();

    void setBoxThreshold(float threshold);
    void setScore(float score);

private:
    ObjectDetector *tf;
    DetectResult* res;
    static volatile float score_;
};
#endif