## Simple Bandcamp cli downloader

### Usage

```bash
bcdl.py [OPTIONS] [OPT_ARGUMENTS] [URL]
```

For downloading album or single track to default folder _'download/'_:
```bash
bcdl.py https://<artist>.bandcamp.com/album/<some_album_name>
```

For downloading all album of artist:
```bash
bcdl.py -a https//<artist>.bandcamp.com 
	or
bcdl.py -a https//<artist>.bandcamp.com/album/<some_album_name> # after '.com' url will sliced
```

For adding numeration to song names:
```bash
bcdl.py -n https://<artist>.bandcamp.com/album/<some_album_name>
```

For changing downloading path:
```bash
bcdl.py -p some/your/download/path/ https://<artist>.bandcamp.com/album/<some_album_name>
```

Or all in one:
```bash
bcdl.py -pan some/your/download/path/ https://<artist>.bandcamp.com/album/<some_album_name>
```


