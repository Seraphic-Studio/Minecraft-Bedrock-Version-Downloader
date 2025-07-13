# Minecraft Bedrock Version Downloader

A Python tool to download Minecraft Bedrock Edition versions directly from Microsoft's servers.

<img src="https://media.discordapp.net/attachments/1209366891051618394/1393588270377734274/image.png?ex=6873b7b7&is=68726637&hm=398d40ab732631e2c2292b6232699c0ed3b6d075c8f790c1136aee16872d7b7f&=&format=webp&quality=lossless" width="auto;" alt="Seraphic Studio"/>

## Features

- Download any Minecraft Bedrock Appx file (Release, Beta, Preview)
- Command-line interface for automation
- Graphical user interface for ease of use
- Search and filter versions by type

## Installation

1. Clone the repository:

```bash
git https://github.com/Seraphic-Studio/Minecraft-Bedrock-Version-Downloader.git
cd minecraft-bedrock-version-downloader
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

List available versions:

```bash
python cli.py --list --type release
```

Search for specific versions:

```bash
python cli.py --search "1.20"
```

Download by version name:

```bash
python cli.py --name "1.20.81.01"
```

Download by UUID:

```bash
python cli.py --download "UUID-HERE"
```

Download beta versions (requires MSA token):

```bash
python cli.py --name "1.21.0.03" --token "YOUR_MSA_TOKEN"
```

### GUI Interface

Run the graphical interface:

```bash
python gui.py
```

## Command Line Options

- `--list`: List available versions
- `--download UUID`: Download version by UUID
- `--name NAME`: Download version by name
- `--type {release,beta,preview}`: Filter by version type
- `--output PATH`: Custom output file path
- `--token TOKEN`: MSA token for beta versions
- `--api URL`: Custom version list API URL
- `--search QUERY`: Search versions by name

## Beta Version Authentication

Beta versions require authentication with Microsoft. You need to:

1. Be subscribed to the Minecraft Beta program
2. Obtain an MSA (Microsoft Account) token
3. Use the `--token` parameter when downloading

## Platform Support

- Windows

## License

This project is licensed under the GPL v3.0 License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

### Common Issues

**"Version not found" error:**

- Verify the version name or UUID is correct
- Check if the version list API is accessible

**Beta download fails(rare):**

- Ensure you have a valid MSA token
- Verify your account is subscribed to the Minecraft Beta program

**Download interrupted:**

- The tool automatically handles resume for incomplete downloads
- Check your internet connection and disk space

### Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with details about your problem

## Credits

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/MCMrARM">
        <img src="https://avatars.githubusercontent.com/u/5191659?v=4" style="border-radius: 50%;" width="30px;" alt="MCMrARM"/><br />
        <sub><b>MCMrARM</b></sub>
      </a>
      <br />
      <a href="https://github.com/MCMrARM/mc-w10-version-launcher"><sub>mc-w10-version-launcher</sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/ddf8196">
        <img src="https://avatars.githubusercontent.com/u/73578766?v=4" style="border-radius: 50%;" width="30px;" alt="ddf8196"/><br />
        <sub><b>ddf8196</b></sub>
      </a>
      <br />
      <a href="https://github.com/ddf8196/mc-w10-versiondb-auto-update"><sub>mc-w10-versiondb-auto-update</sub></a>
    </td>
  </tr>
</table>

## Developers

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/Hiba550">
        <img src="https://avatars.githubusercontent.com/u/132037918?v=4" style="border-radius: 50%;" width="30px;" alt="Hiba550"/><br />
        <sub><b>Hiba550</b></sub>
      </a>
      <br />
      <sub>(aka Not 0x4a4b)</sub>
    </td>
    <td align="center">
      <a href="https://github.com/Jiyath5516F">
        <img src="https://avatars.githubusercontent.com/u/75976630?v=4" style="border-radius: 50%;" width="30px;" alt="Jiyath5516F"/><br />
        <sub><b>Jiyath5516F</b></sub>
      </a>
      <br />
      <sub>(aka 0x4a4b)</sub>
    </td>
  </tr>
</table>

---

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/Seraphic-Studio">
        <img src="https://avatars.githubusercontent.com/u/220401186?s=200&v=4" style="border-radius: 50%;" width="50px;" alt="Seraphic Studio"/><br />
        <sub><b>Seraphic Studio</b></sub>
      </a>
      <br />
    </td>
  </tr>
</table>

---
