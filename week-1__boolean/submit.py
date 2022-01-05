import requests, json
from six.moves import input

DELIMETER = '__SUBMISSIONS_FILE_DELIMETER__'

def pack(files_to_pack):
    data = []
    for file_name in files_to_pack:
        with open(file_name, 'r', encoding="utf-8") as fd:
            data.append(fd.read())
    return DELIMETER.join(data)


def submit(submitterEmail,secret,key,submission_part,all_parts, data):
        submission = {
                    "assignmentKey": key,
                    "submitterEmail":  submitterEmail,
                    "secret":  secret,
                    "parts": {}
                  }
        for part in all_parts:
            if part == submission_part:
                submission["parts"][part] = {"output": data}
            else:
                submission["parts"][part] = dict()

        response = requests.post('https://www.coursera.org/api/onDemandProgrammingScriptSubmissions.v1', data=json.dumps(submission))

        if response.status_code == 201:
            print ("Submission successful, please check on the coursera grader page for the status")
        else:
            print ("Something went wrong, please have a look at the reponse of the grader")
            print ("-------------------------")
            print (response.text)
            print ("-------------------------")



key = "sQh3BRcEEeiUlwrPYUA5dg" # Assessment key found on the authoring side (top of page)
all_parts = ["R5GJE"] # Part IDs found on the authoring side

email =  input("What is your Coursera email?\n")
secret = input("What is your Coursera token? (please find this on the assessment page)\n")

part = "R5GJE"
assignment_files = [ 'index/wrapper.py' ]

data = pack(assignment_files)

submit(email, secret, key, part, all_parts, data)