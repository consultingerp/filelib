# -*- coding: utf-8 -*-
from transform import four_point_transform
import cv2, imutils,numpy
import imgenhance

def preProcess(image):
    ratio = image.shape[0] / 500.0
    image = imutils.resize(image, height=500)

    grayImage  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gaussImage = cv2.GaussianBlur(grayImage, (5, 5), 0)
    edgedImage = cv2.Canny(gaussImage, 75, 200)
    # cv2.imshow("gray", imutils.resize(grayImage, height=500))
    # cv2.imshow("gauss", imutils.resize(gaussImage, height=500))
    # cv2.imshow("edged", imutils.resize(edgedImage, height=500))
    #
    # cv2.destroyAllWindows()
    cnts = cv2.findContours(edgedImage.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[1] if imutils.is_cv3() else cnts[0]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    for c in cnts:
        peri = cv2.arcLength(c, True)  # Calculating contour circumference
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            screenCnt = approx
            break

    return  screenCnt, ratio

if __name__ == "__main__":

    image = cv2.imread("img2.jpg")
    screenCnt, ratio = preProcess(image)
    warped = four_point_transform(image, screenCnt.reshape(4, 2) * ratio)

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