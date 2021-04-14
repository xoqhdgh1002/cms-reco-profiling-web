#

Contents of the http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/web page.
The contents of the web page are described in the [spec.md](spec.md).

## Workflow

- clone this repo
- edit the [web/index.html](web/index.html) file
- preview the changes in your local web space
- once you are done, open a PR with your edits
- once the PR is merged, deploy the webpage to production on lxplus:
```
[lxplus]$ ./deploy.sh
```
Note that the deployment step will overwrite any manual changes to the webpage that are not tracked in git!

## Dependencies

- igprof-navigator: https://github.com/cms-externals/igprof
- circles: https://github.com/fwyzard/circles
 
```
[lxplus]$ ./deploy-deps.sh
```


## Useful links

- CMS reco profiling landing page (WIP): http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/web
- EOS path for profiling data: `/eos/cms/store/user/cmsbuild/profiling`
- EOS path for the webpage: `/eos/project/c/cmsweb/www/reco-prof`
- profiling jenkins jobs: https://cmssdt.cern.ch/jenkins/job/release-run-reco-profiling/
- cmssw bot scripts that run the automatic profiling: https://github.com/cms-sw/cms-bot/tree/master/reco_profiling/
