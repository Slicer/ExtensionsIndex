from urllib2 import urlopen, Request
import json, os, glob, sys

# NB: GitHub will throttle down requests without a personal access token!
# Request yours under GitHub "Settings / Developer settings / Personal access tokens"
# and assign below
token = None

def main():
    # loop over all s4ext in the input directory
    if len(sys.argv) == 1:
        print("Running this script will replace all occurrences of \'master\' for scmrevision\n\
          with the master hash at the time script is run for the repositories hosted on GitHub.\n\
          To do this for all of the s4ext files in the current directory, pass \'all\' as the argument.\n\
          To replace in specific s4ext files, pass the list of files separated by spaces.")
        sys.exit(1)
    elif sys.argv[1] == "all":
        s4extFileNames = glob.glob("*.s4ext")
    else:
        s4extFileNames = sys.argv[1:]

    for s4extName in s4extFileNames:
        print("Processing " + s4extName)

        fileContent = []
        org = None
        repo = None
        originalHash = None
        newHash = None
        onGitHub = False

        # NB: newlines are inconsistent in .s4ext's as of now - we should consider
        #  adding a config file to make new additions consistent going forward:
        #  https://help.github.com/articles/dealing-with-line-endings/#per-repository-settings
        with open(s4extName, 'rU') as s4extFile:
            fileContent = s4extFile.readlines()

        # need to iterate twice, since scmrevision and scmurl don't have to be in order!
        for i in range(len(fileContent)):
            line = fileContent[i][:-1]
            if line.startswith('scmurl') and len(line.split('github.com')) > 1:
                scmurl = line.split(' ')[1]
                if scmurl.find('github.com') != -1:
                    onGitHub = True
                # first character is either '/' for URLs, or ':' for git@github format,
                #  so skip the first character instead of parsing it
                org = scmurl.split('github.com')[1][1:].split('/')[0]
                repo = scmurl.split('github.com')[1][1:].split('/')[1]
                if repo.find('.git') != -1:
                    repo = repo.split('.git')[0]
            if line.startswith('scmrevision'):
                originalHash = line.split(' ')[1]

        if onGitHub and originalHash == 'master':
            url = "/".join(["https://api.github.com/repos", org, repo, "commits", "master"])

            if token:
                request = Request(url, headers={"Authorization": 'token %s' % token})
            else:
                request = Request(url)

            response = urlopen(request)
            responseJson = json.loads(response.read())
            newHash = responseJson["sha"]

        if newHash:
            with open(s4extName, 'w') as s4extFile:
                for line in fileContent:
                    if line.startswith('scmrevision'):
                        print("scmrevision for " + org + "/" + repo + " will be updated from master to " + newHash)
                        s4extFile.write('scmrevison ' + newHash + '\n')
                    else:
                        s4extFile.write(line)

if __name__ == "__main__":
    main()
