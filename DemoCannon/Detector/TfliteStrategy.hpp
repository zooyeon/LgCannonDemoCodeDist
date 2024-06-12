#include "DetectStrategy.hpp"
#include "ObjectDetector.h"

class TfliteStrategy : public DetectStrategy {
public:
    TfliteStrategy();
    virtual ~TfliteStrategy();

    virtual void detect(const cv::Mat& Frame);
    virtual void sync(TDetected (&detected)[], int &numDetected);

private:
    ObjectDetector *tf;
    DetectResult* res;
};