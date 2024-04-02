import cv2 as cv
import face_recognition
import pickle
import os

# Importing student images
folderPath = 'images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []
# print(pathList)
for path in pathList:
    imgList.append(cv.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])
    # print(path)
    # print(os.path.splitext(path)[0])
print(len(imgList))
print(studentIds)


def findEncodings(imageList):
    i = 0
    encodeList = []
    for img in imageList:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        try:
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except Exception:
            i += 1
            print(i)
            pass

    return encodeList

print("Encode Starting")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encode Completed")

file = open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")