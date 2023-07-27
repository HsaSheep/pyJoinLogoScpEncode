
import os
import sys
import re
import configparser
import urllib.request
import urllib.parse
import urllib.error
import subprocess
from tkinter import filedialog

ver = 0.1
conf_path = 'conf/config.ini'
config = configparser.ConfigParser()

default_configs = {
    'My':
        {
            'ver': str(ver),
            'enable': str(bool(False))
        },
    'Path':
        {
            'avi_utl': 'aviutl110/aviutl.exe',
            'avi_utl_controller': 'aviutl110/auc',
            'join_logo_scp': 'join_logo_scp/jlse_bat.bat'
        },
    'Auc':
        {
            'enc_plugin_no': '0'
        },
    'Rename':
        {
            'date_delete': str(bool(False))
        },
    'Line':
        {
            'enable': 'false',
            'key': '0'
        }
}


# ### コンフィグ・パス関係 ###
def save_config():
    print('設定ファイルを保存します。('+conf_path+')')
    if not os.path.isdir(os.path.dirname(conf_path)):
        os.makedirs(os.path.dirname(conf_path))
    with open(conf_path, 'w') as conf_file:
        config.write(conf_file)


def config_check():
    is_file = os.path.isfile(conf_path)
    if is_file:
        print('コンフィグファイルを確認しました。')
    else:
        print('コンフィグファイルがありません。作成します。')
        config.read_dict(default_configs)
        save_config()
    config.read(conf_path)
    my = config['My']
    if my.getboolean('enable') == bool(False):
        print('初期値で作成します。')
        config.set('My', 'enable', str(bool(True)))
        save_config()
    elif my.getfloat('ver') < ver:
        print('コンフィグを読み込みました。('+my.get('ver')+')※古いバージョン設定です。')
        print('変更点があるか確認し、必要に応じてコンフィグを更新します。')
        config.read_dict(default_configs)
        config.read(conf_path)
        config.set('My', 'ver', str(ver))
        save_config()
    else:
        print('コンフィグを読み込みました。('+my.get('ver')+')')


def path_check():
    path = config['Path']
    dir_path = os.getcwd()
    is_ok = bool(True)
    if not os.path.isfile(path.get('avi_utl')):
        print("「avi_utl」のパスが不正です。(aviutl.exe)")
        select_type = [('aviutl.exe', '*.exe')]
        file_path = filedialog.askopenfilename(filetypes=select_type, initialdir=dir_path, title="「aviutl.exe」を選択")
        config.set('Path', 'avi_utl', file_path)
        is_ok = bool(False)
    if not os.path.isdir(path.get('avi_utl_controller')):
        print("「avi_utl_controller」のパスが不正です。(aucフォルダ)")
        folder_path = filedialog.askdirectory(initialdir=dir_path, title="「auc」フォルダを選択")
        config.set('Path', 'avi_utl_controller', folder_path)
        is_ok = bool(False)
    if not os.path.isfile(path.get('join_logo_scp')):
        print("「join_logo_scp」のパスが不正です。(jlse_bat.bat)")
        select_type = [('jlse_bat.bat', '*.bat')]
        file_path = filedialog.askopenfilename(filetypes=select_type, initialdir=dir_path, title="「jlse_bat.bat」を選択")
        config.set('Path', 'join_logo_scp', file_path)
        is_ok = bool(False)
    if is_ok == bool(True):
        print("パスのチェック完了。")
        save_config()
    else:
        path_check()


# ### 処理状況通知関係 ###
def notifire_encode_start(filename, count=1, total=1):
    message = str(count) + "/" + str(total) + "「" + filename + "」処理開始"
    print(message)
    line_notifire(message)


# ### LINE通知関係 ###
def line_key_set(key):
    config.set('Line', 'key', str(key))
    line_notifire_test()


def line_notifire_test():
    print('Lineテスト実行')
    status = line_notifire('test!テスト！', bool(True))
    if status == bool(True):
        print('Line通知成功。有効化します。')
        config.set('Line', 'enable', str(bool(True)))
    else:
        print('Line通知失敗。無効化します。Keyの値が正しいか確認してください。')
        config.set('Line', 'enable', str(bool(False)))
        # config.set('line', 'key', str()) # 消すと戻せなくなるので一応そのままにすることに


def line_notifire(message, test=bool(False)):
    if (test == bool(True)) or (config.getboolean('Line', 'enable') == bool(True)):
        line = config['Line']
        status = line_notifire_send(line.get('key'), message)
        if test == bool(False):
            if status == bool(True):
                print('Line通知しました。')
            else:
                print('Line通知は無効または失敗しました。通知テストします。')
                line_notifire_test()
        return status


def line_notifire_send(key, message):
    payload = {
        'message': message
    }
    payload = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request('https://notify-api.line.me/api/notify', data=payload)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Authorization', 'Bearer ' + key)
    status = url_post(req)
    return status


def url_post(request):
    request.get_method = lambda: 'POST'
    http_ok = bool(False)
    try:
        with urllib.request.urlopen(request) as res:
            body = res.read()
            print('HTTP Response: ' + str(body))
            http_ok = bool(True)
    except urllib.error.HTTPError as e:
        config.set('Line', 'enable', str(bool(False)))
        print('HTTP Error: ' + str(e))
    return http_ok


# ### 対象選択・パス変換 ###
def select_target_file(target_folder_path=""):
    if not target_folder_path == "":
        if os.path.isdir(target_folder_path) == bool(False):
            target_folder_path = ""
    if target_folder_path == "":
        target_folder_path = os.getcwd()
    print("変換対象のファイルを選択してください。")
    select_type = [('*.ts, *.m2ts', '*.ts;*.m2ts')]
    return filedialog.askopenfilename(filetypes=select_type, initialdir=target_folder_path,
                                      title="「変換対象ファイル(.ts .m2ts)」を選択")


def select_target_files(target_folder_path=""):
    if not target_folder_path == "":
        if os.path.isdir(target_folder_path) == bool(False):
            target_folder_path = ""
    if target_folder_path == "":
        target_folder_path = os.getcwd()
    print("変換対象のファイルを選択してください。")
    select_type = [('*.ts, *.m2ts', '*.ts;*.m2ts')]
    select_files_path = filedialog.askopenfilenames(filetypes=select_type, initialdir=target_folder_path,
                                                    title="「変換対象ファイル(.ts .m2ts)」を選択")
    total = len(select_files_path)
    select_files_path = sorted(select_files_path, key=lambda p: p.split('/'[-1]))
    return select_files_path


def file_rename(target_file_path):
    change_path = target_file_path
    # ファイル名の全角空白を削除
    change_path = os.path.dirname(change_path) + "/" + os.path.basename(change_path).replace('　', ' ')
    # ファイル名末尾の空白を削除
    while os.path.splitext(os.path.basename(change_path))[0][-1:] == " ":
        change_path = os.path.splitext(change_path)[0][:-1] + os.path.splitext(change_path)[1]
    # .m2tsを.tsに置換
    if os.path.splitext(change_path)[1] == ".m2ts":
        change_path = os.path.splitext(change_path)[0] + ".ts"
        print("4." + str(change_path))
    # 元のパスから変更がある場合、表示しリネーム
    if not target_file_path == change_path:
        print("ファイル名を変更します。： " + os.path.basename(change_path))
        os.rename(target_file_path, change_path)
    return change_path


def file_path2avs_path(target_file_path):
    if not os.path.isfile(target_file_path):
        print("ファイルが見つかりません。")
        return ""
    f_name = str(os.path.dirname(config['Path']['join_logo_scp']))
    f_name += "/result"
    f_name += "/" + str(os.path.splitext(os.path.basename(target_file_path))[0])
    f_name += "/in_cutcm_logo.avs"
    return f_name


# ### JoinLogoSCP関係 ###
def run_join_logo_scp(target_file_path):
    print("JoinLogoSCPによる処理開始")
    cmd_file = config['Path']['join_logo_scp']
    subprocess.run([cmd_file, target_file_path], encoding='cp932',
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("処理終了。")


# ### AviUtl Controller関係 ###
def run_avi_utl_controller(target_file_path):
    print("AviUtlによるエンコード開始")
    mp4_filepath = os.path.dirname(target_file_path)
    # configのRename内mp4_filename_date_deleteがTrueの場合、年月日を確認し削除
    if config.getboolean('Rename', 'mp4_filename_date_delete') == bool(True):
        mp4_filename = os.path.basename(mp4_filepath)
        mp4_filename_tmp = mp4_filename
        pattern = r'\d{4}[年/]\d{1,2}[月/]\d{1,2}日?'
        res = re.findall(pattern, mp4_filename)
        mp4_filename = mp4_filename.replace(res[0], '')
        # 日付を削除したことにより、先頭の文字が下記になった場合、該当しなくなるまで削除
        pattern = ['-', ' ']
        count = 0
        while count <= len(pattern):
            for pat in pattern:
                if mp4_filename[0] == pat:
                    mp4_filename = mp4_filename[1:]
                    count = 0
                else:
                    count += 1
        print(mp4_filepath)
        print(mp4_filename)
        print(mp4_filename_tmp)
        mp4_filepath = mp4_filepath[:-1*len(mp4_filename_tmp)] + mp4_filename
        print(mp4_filepath)
        print(".mp4ファイル名から日付を削除しました。 : " + os.path.basename(mp4_filepath))
    mp4_filepath += ".mp4"
    exe_dir = config['Path']['avi_utl_controller']
    res = subprocess.run([exe_dir + "/auc_exec.exe", config['Path']['avi_utl']], encoding='cp932',
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    w_id = str(res.returncode)
    print("WindowID: "+str(w_id))
    subprocess.run([exe_dir + "/auc_open.exe", w_id, target_file_path.replace('/', chr(ord('\\')))])
    subprocess.run([exe_dir + "/auc_plugout.exe", w_id, config['Auc']['enc_plugin_no'],
                    mp4_filepath.replace('/', chr(ord('\\')))])
    subprocess.run([exe_dir + "/auc_wait.exe", w_id])
    subprocess.run([exe_dir + "/auc_close.exe", w_id])
    print("エンコード終了。")


# ### 実行ルーティン関係 ###
def run_jlscp_auc(target_files_path):
    total = len(target_files_path)
    for i, filepath in enumerate(target_files_path):
        filepath = file_rename(filepath)
        #notifire_encode_start(os.path.splitext(os.path.basename(filepath))[0], i+1, total)
        #run_join_logo_scp(filepath)
        avs_filepath = file_path2avs_path(filepath)
        run_avi_utl_controller(avs_filepath)


# ### メイン関係 ###
if __name__ == '__main__':
    config_check()
    path_check()
    # line_notifire_test()
    # ### 引数があるか確認
    argvs = sys.argv
    argc = len(argvs)
    if argc == 1:
        files_path = select_target_files()
        if not files_path == "":
            run_jlscp_auc(files_path)
    else:
        print("引数あり")
