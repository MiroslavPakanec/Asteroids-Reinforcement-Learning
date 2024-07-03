FROM pytorch/pytorch:2.3.1-cuda11.8-cudnn8-devel
WORKDIR /workspace

ENV PATH="/home/asteroids/.local/bin:$PATH"
RUN apt update
RUN apt install python3 python3-pip -y
RUN apt install x11-apps -y

COPY requirements.txt requirements.txt
RUN pip install --disable-pip-version-check -r requirements.txt

COPY . .
CMD ["/bin/bash", "./scripts/run_game.sh"]