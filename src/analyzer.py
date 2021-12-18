from collections import defaultdict
from nltk.sentiment import SentimentIntensityAnalyzer
from plotly.subplots import make_subplots
from tqdm import tqdm
import json
import nltk
import plotly.graph_objects as go
import demoji
import sys

analyzer = SentimentIntensityAnalyzer()


def init():
    nltk.download("vader_lexicon")


def checkIfContainsX(source):
    return "shib" in source.lower() or "doge" in source.lower()


def getMessageFromList(messageList):
    output = ""
    for message in messageList:
        output += message if isinstance(message, str) else message["text"]


def getDataFromFile(fileName):
    data = ""
    with open(fileName, "r") as readFile:
        data = json.load(readFile)
    messages = data["messages"]
    return messages


def isEnglish(message):
    return message.isascii()


def handleEmoji(message):
    return demoji.replace_with_desc(message, sep="")


def analyze(dayMessages):
    daySentimentDistribution = defaultdict(float)
    for k, v in dayMessages.items():
        for message in v:
            daySentimentDistribution[k] += analyzer.polarity_scores(message)[
                "compound"]
        daySentimentDistribution[k] = daySentimentDistribution[k]/len(v)
    return daySentimentDistribution


def analyzeWithoutNeutral(dayMessages):
    daySentimentDistribution = defaultdict(float)
    for k, v in dayMessages.items():
        total = 0
        for message in v:
            score = analyzer.polarity_scores(message)["compound"]
            if score != 0:
                daySentimentDistribution[k] += analyzer.polarity_scores(message)[
                    "compound"]
                total += 1
        daySentimentDistribution[k] = daySentimentDistribution[k]/total
    return daySentimentDistribution


def getDistribution(messages):
    dayMessages = defaultdict(list)
    for index in tqdm(range(len(messages))):
        message = messages[index]
        try:
            if isinstance(message["text"], list):
                for subMessage in message:
                    messageStr = handleEmoji(subMessage if isinstance(
                        subMessage, str) else subMessage["text"])
                    if isEnglish(messageStr) and checkIfContainsX(messageStr):
                        dayMessages[message["date"][:10]].append(
                            getMessageFromList(message))
                        break
            else:
                messageStr = handleEmoji(message["text"])
                if isEnglish(messageStr) and checkIfContainsX(messageStr):
                    dayMessages[message["date"][:10]].append(messageStr)
        except:
            print(type(message))
    return dayMessages


def buildPlots(daySentimentDistribution):
    fig = make_subplots(rows=2, cols=1, specs=[
                        [{"type": "scatter"}], [{"type": "scatter"}]])
    fig.add_trace(go.Scatter(x=list(daySentimentDistribution.keys()), y=list(daySentimentDistribution.values()),
                             name="day vs sentiment trend from a scale of -1 to 1", line_shape='linear'), row=1, col=1)
    fig.add_trace(go.Scatter(x=list(dayMessageDistribution.keys()),
                             y=list([len(v) for v in dayMessageDistribution.values()]), name="day vs number of messages", line_shape='linear'), row=2, col=1)
    return fig


if __name__ == "__main__":
    init()
    fileName = sys.argv[-1] if "--file" in sys.argv else "data/data.json"
    messages = getDataFromFile(fileName)
    dayMessageDistribution = getDistribution(messages)

    daySentimentDistribution = analyzeWithoutNeutral(
        dayMessageDistribution) if "--exclude-neutral" else analyze(dayMessageDistribution)
    if "--trace" in sys.argv:
        for k, v in daySentimentDistribution.items():
            print("date: ", k, " sentiment score (between -1 and 1): ", v)
    buildPlots(daySentimentDistribution).show()
