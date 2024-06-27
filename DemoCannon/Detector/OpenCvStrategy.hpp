#include "DetectStrategy.hpp"

class OpenCvStrategy : public DetectStrategy {
public:
    OpenCvStrategy();
    virtual ~OpenCvStrategy();

    virtual void detect(const cv::Mat& Frame);
    virtual void sync(TDetected (&detected)[], int &numDetected);
    void setMinDiffThreshold(double minDiffThreshold);
private:
    double minDiffThreshold = 1500000;
};