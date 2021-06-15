from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
import cloudscraper

app = Flask(__name__)

# client = MongoClient('mongodb://id:pw@ip'27017)
client = MongoClient('3.35.210.207', 27017, username="test", password="test")
db = client.dbsparta_plus_week2


@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    msg = request.args.get("msg")
    words = list(db.words.find({}, {"_id": False}))
    return render_template("index.html", words=words, msg=msg)


@app.route('/detail/<keyword>')
def detail(keyword):
    status_receive = request.args.get("status_give")
    # API에서 단어 뜻 찾아서 결과 보내기
    scraper = cloudscraper.create_scraper()
    headers = {
        "Authorization": "Token fcc9b92dd9a033a6f712280ba95093d8c41dba67",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }
    r = scraper.get(f"https://owlbot.info/api/v4/dictionary/{keyword}?format=json", headers=headers)

    if r.status_code != 200:
        return redirect(url_for("main", msg="제대로 된 단어를 입력해라"))
    result = r.json()
    print(result)
    return render_template("detail.html", word=keyword, result=result, status=status_receive)
    # result 라는 이름으로 사전 Api 에서 가져온 값을 html에 보내준다


@app.route('/api/save_word', methods=['POST'])
def save_word():
    # 단어 저장하기
    word_receive = request.form["word_give"]
    definition_receive = request.form["definition_give"]
    doc = {"word": word_receive, "definition": definition_receive}
    db.words.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f'단어 {word_receive} 저장'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    # 단어 삭제하기
    word_receive = request.form["word_give"]
    db.words.delete_one({"word": word_receive})
    return jsonify({'result': 'success', 'msg': f'단어 {word_receive} 삭제'})

# 내가 지금 api를 만든 것임
@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    # 예문 가져오기
    word_receive = request.args.get("word_give")
    # // get 요청이니까 args로 보내줌
    result = list(db.examples.find({'word': word_receive}, {'_id': False}))
    return jsonify({'result': 'success', 'examples': result})
# http://localhost:5000/api/get_exs?word_give=good 이 url로 확인해 볼 수 있음

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    # 예문 저장하기
    word_receive = request.form["word_give"]
    example_receive = request.form["example_give"]

    doc = {
        "word": word_receive,
        "example": example_receive
    }
    db.examples.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '예문 저장 완료!'})


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    # 예문 삭제하기
    word_receive = request.form["word_give"]
    number_receive= int(request.form["number_give"])
    example = list(db.examples.find({"word": word_receive}))[number_receive]["example"]
    print(word_receive, example)
    db.examples.delete_one({"word": word_receive, "example": example})
    return jsonify({'result': 'success', 'msg': f'예문 of "{word_receive}" 삭제됨'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
