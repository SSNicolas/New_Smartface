import cv2 as cv
import face_recognition

cap = cv.VideoCapture(0)
cap.set(3,1280)
cap.set(4, 720)



while True:
    sucess, img = cap.read()
    cv.imshow("Webcam", img)
    cv.waitKey(1)























# # Carregue as imagens conhecidas e crie os encodings
# known_image_1 = face_recognition.load_image_file("images/eu1.jpg")
# known_image_1_encoding = face_recognition.face_encodings(known_image_1)[0]
#
# known_image_2 = face_recognition.load_image_file("images/mazon1.jpg")
# known_image_2_encoding = face_recognition.face_encodings(known_image_2)[0]
#
# # Lista de encodings e seus respectivos nomes
# known_face_encodings = [known_image_1_encoding, known_image_2_encoding]
# known_face_names = ["nicolas", "mazon"]
#
# # Inicialize a captura de vídeo
# video_capture = cv2.VideoCapture(0)
#
# while True:
#     # Capture frame-a-frame
#     ret, frame = video_capture.read()
#
#     # Converta a imagem de BGR (que o OpenCV usa) para RGB (que face_recognition usa)
#     rgb_frame = frame[:, :, ::-1]
#
#     # Encontre todos os rostos e encodings no frame atual do vídeo
#     face_locations = face_recognition.face_locations(rgb_frame)
#     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#
#     for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#         # Veja se a face é uma correspondência para as faces conhecidas
#         matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#
#         name = "Desconhecido"
#
#         # Se houver uma correspondência, use a primeira.
#         if True in matches:
#             first_match_index = matches.index(True)
#             name = known_face_names[first_match_index]
#
#         # Desenha um retângulo em volta da face
#         cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
#
#         # Desenha um label com um nome abaixo da face
#         cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
#         font = cv2.FONT_HERSHEY_DUPLEX
#         cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
#
#     # Exibe o resultado
#     cv2.imshow('Vídeo', frame)
#
#     # Aperte 'q' para sair do loop
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Quando tudo estiver feito, libere a captura
# video_capture.release()
# cv2.destroyAllWindows()
