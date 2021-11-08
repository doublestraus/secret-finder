<img src="https://img.shields.io/badge/Python-3.8-green"> <img src="https://img.shields.io/badge/License-Apache%202.0-blue"> <img src="https://img.shields.io/badge/Status-Beta-orange"> <img src="https://img.shields.io/github/commit-activity/m/doublestraus/secret-finder"> <img src="https://img.shields.io/github/languages/code-size/doublestraus/secret-finder">

# Secret scanner

## Description

Find secrets in Redmine, Confluence, Jira

## Roadmap

- [ ] Scoring tuning for password search
- [ ] HTML reporting
- [ ] Notions search support
- [ ] DefectDojo integration polish
- [ ] Config check
- [ ] Chunk control
- [ ] Change config format to yaml

## Installation

Create "out" folder inside the project for reports<br />
```pip install -r requirements.txt```

## Configuration config.json

<b>re_scan</b> - word root search (badrootlist)<br />
<b>uuid_scan</b> - uuid4 search <br />
<b>twartefacts_scan</b> - teamviewer id search (9 and 10 length, starts with 1)<br />
<b>gdocs_search</b> - search google docs links<br />
<b>experimental_scan</b> -  Levenshtein distance comparison (todo)<br />
<b>context_capture_span</b> - context capture for rescan module (50 symbols left and right from the match) <br />
<b>notifications</b> - notifications for MyTeam and DefectDojo(todo)<br />
<b>Аrray spaces</b> - partial scan support, scans only selected spaces in jira and confluence (saves time)

```
{
  "base_config": {
    "timeout": 30,
    "re_scan": true,
    "uuid_scan": true,
    "twartefacts_scan": true,
    "gdocs_search": true,
    "experimental_scan": false,
    "context_capture_span": 50,
    "notifications": {
      "myteam": {
        "enabled": false,
        "bot_id": "",
        "bot_secret": "",
        "channel_id": ""
      },
      "defectDojo": {
        "enabled": false,
        "defectDojo_url": "",
        "api_key": ""
      }
    }
  },

  "redmine": {
    "url": "https://tracker.site",
    "credentials": {
      "login": "",
      "password": ""
    }
  },
  "confluence": {
    "url": "https://confluence.site",
    "oauth: false,
    "spaces": [],
    "credentials": {
      "login": "",
      "password": ""
    },
  "jira": {
     "url": "https://jira.site",
     "oauth": false,
     "spaces": [],
     "credentials" : {
       "login": "",
       "password": ""
     }
   },
  },
  "lists":{
    "badlist": ["пароль", "токен", "password", "pass", "учетка",
           "credentials", "ключ", "token", "licensetoken",
           "guid", "LicenseInfo", "tw"],
    "badrootlist": ["парол", "токен", "pass", "license", "credentials", "token"]
  }
}
```

## Usage
Jira
```
python3 main.py --config="config.json" --jira --debug
```
Сonfluence
```
python3 main.py --config="config.json" --confluence --debug
```
Redmine
```
python3 main.py --config="config.json" --redmine --debug
```
## Version
0.2
