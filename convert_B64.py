import base64
frame_Id = "ebfd83df-8c14-4ad1-b8ca-df9b8c0e7e3c"
path_Img_Process = "img/frame _processed/frame_out/%s.png" % (frame_Id)
with open(path_Img_Process, "rb") as img_file:
    b64_string = base64.b64encode(img_file.read())
print(b64_string)
