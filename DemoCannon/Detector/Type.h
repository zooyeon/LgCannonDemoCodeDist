#pragma once

#include <opencv2/core.hpp>

typedef struct NDetected
{
    int     match = -1;
    cv::Point2f center = { 0,0 };
    float   ymin = 0.0;
    float   xmin = 0.0;
    float   ymax = 0.0;
    float   xmax = 0.0;
    cv::String label;
} TDetected;