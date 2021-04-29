# bot
Hypserver Slack bot for fun and stuff


## Devlopment
### Install python poetry, and create an env:

```bash
poetry env use python3.8
```

### Activate env
```bash
poetry shell
```

### Install requriements
```bash
poetry install --dev
```

## Deploy
Either create a PR to master 🤩 or just push to master ¯\\\_(ツ)\_/¯  😂, Google Cloud Build handles the rest.


## Features
- Detect images with faces, project one side of the face to the other and post back to `#sapsik` channel.
- gsheet archiving
  - Archive pinned items to a gsheet
  - Nightly archive to gsheet for links(atm `#linx` only)
  - When mentioned in a thread with some keywords, archive the original message to gsheet
- Quick replies
  - `sheetle` ask for the sheet that stores the archived content.



## TODO

- [ ] Add some tests
- [ ] Cleanup the code and move some regularly used stuff to helper functions
- [ ] M0ar Features!
