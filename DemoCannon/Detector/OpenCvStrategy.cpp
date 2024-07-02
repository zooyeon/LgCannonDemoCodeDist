#include "OpenCvStrategy.hpp"
#include "CvImageMatch.h"

OpenCvStrategy::OpenCvStrategy(){
    printf("Image Match Mode\n");

    DetectedMatches = new TDetectedMatches[MAX_DETECTED_MATCHES];

    if (LoadRefImages(symbols) == -1) 
    {
        printf("Error reading reference symbols\n");
    }
};

OpenCvStrategy::~OpenCvStrategy() {
};

void OpenCvStrategy::detect(const cv::Mat& Frame) {
    FindTargets(Frame, minDiffThreshold, minContourArea, maxContourArea);
};

void OpenCvStrategy::sync(TDetected (&detected)[], int &numDetected) {
    numDetected = NumMatches;

    for (int i = 0; i < NumMatches; ++i) {
        detected[i].center = DetectedMatches[i].center;
        detected[i].match = DetectedMatches[i].match;
        detected[i].xmin = DetectedMatches[i].xmin;
        detected[i].xmax = DetectedMatches[i].xmax;
        detected[i].ymin = DetectedMatches[i].ymin;
        detected[i].ymax = DetectedMatches[i].ymax;
        detected[i].label = symbols[DetectedMatches[i].match].name;
    }
};

void OpenCvStrategy::setMinDiffThreshold(double minDiffThreshold) {
    this->minDiffThreshold = minDiffThreshold;
};

void OpenCvStrategy::setMinContourArea(double minContourArea) {
    this->minContourArea = minContourArea;
};

void OpenCvStrategy::setMaxContourArea(double maxContourArea) {
    this->maxContourArea = maxContourArea;
};

int OpenCvStrategy::getType() {
    return 0;
}