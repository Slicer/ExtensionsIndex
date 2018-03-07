from urllib2 import urlopen, Request
import json, os, glob

token = "my personal access token - GitHub will throttle down requests without it"
headers = {"Authorization": 'token %s' % token}

def main():
  # loop over all s4ext in the input directory
  for s4extName in glob.glob("*.s4ext"):

    print("Processing "+s4extName)

    fileContent = []
    org = None
    repo = None
    hash = None

    with open(s4extName,'r') as s4extFile:
      fileContent = s4extFile.readlines()

    # need to iterate twice, since scmrevision and scmurl don't have to be in order!
    for i in range(len(fileContent)):
      line = fileContent[i][:-1]
      if line.startswith('scmurl') and len(line.split('github.com'))>1:
        scmurl = line.split(' ')[1]
        # first character is either '/' for URLs, or ':' for git@github format,
        #  so skip the first character instead of parsing it
        org = scmurl.split('github.com')[1][1:].split('/')[0]
        repo = scmurl.split('github.com')[1][1:].split('/')[1]
        if repo.endswith('.git'):
          repo = repo[:-4]

    for i in range(len(fileContent)):
      line = fileContent[i][:-1]
      if line.startswith('scmrevision') and line.split(' ')[1] == 'master':
        url = "/".join(["https://api.github.com/repos",org,repo,"commits","master"])

        # NB: GitHub will throttle down requests without using a personal access token!
        # Request one for free under your GitHub "Settings / Developer settings / Personal access tokens"
        if headers:
          request = Request(url, headers=headers)
        else:
          request = Request(url)
        response = urlopen(request)
        responseJson = json.loads(response.read())
        hash = responseJson["sha"]
        print("scmrevision for "+org+"/"+repo+" will be updated from master to "+hash)
        fileContent[i] = "scmrevision "+hash

    if hash:
      with open(s4extName,'w') as s4extFile:
        for line in fileContent:
          s4extFile.write(line)

if __name__ == "__main__":
  main()
