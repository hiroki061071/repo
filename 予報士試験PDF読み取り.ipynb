import os
import PyPDF2
import cx_Oracle

# PDFファイルをバイナリ形式で開く
with open(r'C:/Users/user/Documents/Bluetooth Folder移管/気象予報士/過去問/第41回/第41回学科（一般）.pdf', 'rb') as f:
    # PDFファイルの読み込み
    pdf = PyPDF2.PdfReader(f)
    # PDFファイル内のページ数を取得
    num_pages = len(pdf.pages)

    # 結果を格納するリストを初期化
    results = []

    # 各ページの処理
    for i in range(num_pages):
        # ページを抽出
        page = pdf.pages[i]
        # ページ内のテキストを取得
        text += page.extract_text()
        print(text)
        # 問題文と選択肢の部分のテキストを抽出
        question_text = text.split('問')[1].split('\n')[0]
        choices = text.split('①')[1].split('\n')
        # 正しい選択肢のインデックスを求める
        correct_answer_index = -1
        for j in range(len(choices)):
            if '正' in choices[j]:
                correct_answer_index = j
                break
        # 結果をリストに追加
        results.append({'question_text': question_text, 'choices': choices, 'correct_answer_index': correct_answer_index})
        # 1ページを読み取ったら処理を停止
        break
        
        # ページごとに結果を表示
        print('問題', len(results))
        print(question_text)
        print('選択肢:')
        for j, choice in enumerate(choices):
            print(f'{j+1}. {choice}')
        print(f"正解: {correct_answer_index+1}")
        print('-' * 20)
    
        # 1ページずつ処理するため、処理が終わったらループを抜ける
        break
