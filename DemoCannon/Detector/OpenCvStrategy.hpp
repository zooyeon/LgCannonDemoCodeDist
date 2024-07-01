#include "DetectStrategy.hpp"

class OpenCvStrategy : public DetectStrategy {
public:
    OpenCvStrategy();
    virtual ~OpenCvStrategy();

    virtual void detect(const cv::Mat& Frame);
    virtual void sync(TDetected (&detected)[], int &numDetected);
    void setMinDiffThreshold(double minDiffThreshold);
    void setMinContourArea(double minContourArea);
    void setMaxContourArea(double maxContourArea);
private:
    double minDiffThreshold = 1000000;
    double minContourArea = 1000;
    double maxContourArea = 30000;
};