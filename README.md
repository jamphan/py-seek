# PySeek

(Under construction)

<!-- TOC depthFrom:2 -->

1. [Usage](#usage)
    1. [Running the Examples](#running-the-examples)
    2. [Running Test](#running-test)

<!-- /TOC -->


## Usage

Install dependencies:

```
pip install -r requirements.txt
```

### Running the Examples

Create a credentials file first:

```
touch config/credentials.yml
echo "username: <username>" > config/credentials.yml
echo "password: <password>" > config/credentials.yml
```

```
cd pyseek
python ./example.py
```

### Running Test

```
cd pyseek
python -m pytest
```