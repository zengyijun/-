import blue_client
import json

# info = '{"client name" : "pi_car1", "00000071":"30", "00000072":"31"}'
f = open("tmpfile/1.txt", "w")
# json.dump(info, f)
f.writelines(["hello\n","world\n","pi\n","car"])
f.close()

blue_client.con_s()
blue_client.send_data("tmpfile/123.txt")
