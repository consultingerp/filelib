# -*- coding: utf-8 -*-
import transform
import cv2, imutils,numpy
import imgenhance

def preProcess(image):
    ratio = image.shape[0] / 500.0
    image = imutils.resize(image, height=500)
    blurredImage = cv2.medianBlur(image, 5)
    grayImage  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gaussImage = cv2.GaussianBlur(grayImage, (5, 5), 0)
    # edgedImage = cv2.Canny(gaussImage, 1, 10)
    edgedImage = cv2.Canny(grayImage, 1, 10)

    sobelx = cv2.Sobel(grayImage, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(grayImage, cv2.CV_64F, 0, 1, ksize=3)
    sobelXY = cv2.Sobel(grayImage, cv2.CV_64F, 1, 1, ksize=3)
    # Parameters for Hough Transform
    rho = 1
    theta = numpy.pi / 180
    threshold = 60
    min_line_length = 100
    max_line_gap = 5

    # Creating an image copy to draw lines on
    line_image = numpy.copy(image)

    # Run Hough on the edge-detected image
    lines = cv2.HoughLinesP(edgedImage, rho, theta, threshold, numpy.array([]),
                            min_line_length, max_line_gap)

    # Iterate over the output "lines" and draw lines on the image copy
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)

    cv2.imshow("Hough", imutils.resize(line_image, height=500))
    # edgedImage = cv2.dilate(edgedImage,numpy.ones((3, 3), numpy.uint8), iterations=2)
    # edgedImage = cv2.erode(edgedImage, numpy.ones((2, 2), numpy.uint8), iterations=3)

    # edgedImage = cv2.Canny(gaussImage, 1, 10)
    cv2.imshow("blurredImage", imutils.resize(blurredImage, height=500))
    cv2.imshow("gray", imutils.resize(grayImage, height=500))
    cv2.imshow("edged70_100", imutils.resize(edgedImage, height=500))
    cv2.Laplacian(grayImage, cv2.CV_8U, grayImage, ksize=3)
    cv2.imshow('laplacian', grayImage)
    def doCanny(x):
        position = cv2.getTrackbarPos("CannyBar", "Canny")
        canny = cv2.Canny(grayImage, position, position * 2.5)
        cv2.imshow("Canny", canny)

    cv2.namedWindow("Canny")

    cv2.createTrackbar("CannyBar", "Canny", 1, 100, doCanny)


    normalizedInverseAlpha = (1.0 / 255) * (255 - grayImage)
    cv2.imshow('normalizedInverseAlpha', normalizedInverseAlpha)
    cv2.imshow('sobelx', sobelx)
    cv2.imshow('sobely', sobely)
    cv2.imshow('sobelxy', sobelXY)
    ret, thresh = cv2.threshold(grayImage, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # 寻找二值化图中的轮廓
    image1, contours = cv2.findContours(
        grayImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    draw_img0 = cv2.drawContours(image, [numpy.array(contours).reshape((-1, 1, 2)).astype(numpy.int32)], 0, (0, 0, 255),
                                 2)
    cv2.imshow("contours", imutils.resize(draw_img0, height=500))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cnts = cv2.findContours(grayImage.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # cnts = cnts[1] if imutils.is_cv3() else cnts[0]
    cnts = sorted(cnts[0], key=cv2.contourArea, reverse=True)

    for c in cnts:
        peri = cv2.arcLength(c, True)  # Calculating contour circumference
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            screenCnt = approx
            cv2.polylines(image, screenCnt, 1, 255);
    cv2.imshow("line", imutils.resize(image, height=500))
    return  screenCnt, ratio

if __name__ == "__main__":

    image = cv2.imread("img3.jpeg")
    screenCnt, ratio = preProcess(image)
    warped = transform.four_point_transform(image, screenCnt.reshape(4, 2) * ratio)

    enhancer = imgenhance.Enhancer()
    enhancedImg = enhancer.gamma(warped,1.63)
    gammaImg0_5 = enhancer.gamma(warped,0.5)
    gammaImg1_0 = enhancer.gamma(warped, 1.0)
    gammaImg2_0 = enhancer.gamma(warped, 2.0)
    cv2.imshow("org", imutils.resize(image, height=500))
    cv2.imshow("warped", imutils.resize(warped, height=500))
    cv2.imshow("gamma1.6", imutils.resize(enhancedImg, height=500))
    cv2.imshow("gamma0.5", imutils.resize(gammaImg0_5, height=500))
    cv2.imshow("gamma1.0", imutils.resize(gammaImg1_0, height=500))
    cv2.imshow("gamma2.0", imutils.resize(gammaImg2_0, height=500))
    cv2.waitKey(0)
    cv2.destroyAllWindows()