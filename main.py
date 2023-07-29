
import os
import sys
import re
import datetime
import threading
import subprocess
import configparser
import urllib.parse
import urllib.error
import urllib.request
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import values

ver = values.EXE_VER
CONF_PATH = 'conf/config.ini'
config = configparser.ConfigParser()
DATE_TIME = datetime.datetime.now()
LOG_FOLDER = 'log/'
LOG_FILENAME = DATE_TIME.strftime('%Y%m%d_%H%M%S') + ".log"
selected_files_list = []
line_token = ""
tk_enable = False


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
            'mp4_filename_date_delete': str(bool(False))
        },
    'Line':
        {
            'enable': 'false',
            'token': '0',
            'minimum': 'False'
        }
}


# ### コンフィグ・パス・ログ関係 ###
def save_config():
    psl('設定ファイルを保存します(' + CONF_PATH + ')')
    if not os.path.isdir(os.path.dirname(CONF_PATH)):
        os.makedirs(os.path.dirname(CONF_PATH))
    with open(CONF_PATH, 'w') as conf_file:
        config.write(conf_file)


def save_log(log_message, file_name=LOG_FILENAME):
    if not os.path.isdir(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    with open(LOG_FOLDER+file_name, 'a', encoding='utf-8') as f:
        f.write(str(log_message)+"\n")


def psl(message, log_file_name=""):
    print(message)
    if log_file_name == "":
        save_log(message)
    else:
        save_log(message, log_file_name)


def p_time(start, end):
    diff_s = str(end - start)
    return diff_s[:diff_s.find('.')]


def config_plugin_no(number=str(0)):
    if isinstance(int(number), int):
        config.set('Auc', 'enc_plugin_no', number)
        psl("出力プラグインを設定: " + config.get('Auc', 'enc_plugin_no'))
    else:
        psl("出力プラグインは整数を入力してください。現在値: " + config.get('Auc', 'enc_plugin_no'))


def config_check():
    is_file = os.path.isfile(CONF_PATH)
    if is_file:
        psl('コンフィグファイルを確認しました')
    else:
        psl('コンフィグファイルがありません-> 作成します')
        config.read_dict(default_configs)
        save_config()
    config.read(CONF_PATH)
    my = config['My']
    if my.getboolean('enable') == bool(False):
        psl('初期値で作成します。')
        config.set('My', 'enable', str(bool(True)))
        save_config()
    elif my.getfloat('ver') < ver:
        psl('コンフィグを読み込みました('+my.get('ver')+')※古いバージョン設定です')
        psl('変更点があるか確認し、必要に応じてコンフィグを更新します')
        config.read_dict(default_configs)
        config.read(CONF_PATH)
        config.set('My', 'ver', str(ver))
        save_config()
    else:
        psl('コンフィグを読み込みました('+my.get('ver')+')')


def path_check():
    path = config['Path']
    dir_path = os.getcwd()
    is_ok = bool(True)
    if not os.path.isabs(path.get('avi_utl')):
        config.set('Path', 'avi_utl', os.path.abspath(path.get('avi_utl')))
    if not os.path.isfile(path.get('avi_utl')):
        psl("「avi_utl」のパスが不正です(aviutl.exe)")
        select_type = [('aviutl.exe', '*.exe')]
        file_path = filedialog.askopenfilename(filetypes=select_type, initialdir=dir_path, title="「aviutl.exe」を選択")
        config.set('Path', 'avi_utl', file_path)
        is_ok = bool(False)
    if not os.path.isabs(path.get('avi_utl_controller')):
        config.set('Path', 'avi_utl_controller', os.path.abspath(path.get('avi_utl_controller')))
    if not os.path.isdir(path.get('avi_utl_controller')):
        psl("「avi_utl_controller」のパスが不正です(aucフォルダ)")
        folder_path = filedialog.askdirectory(initialdir=dir_path, title="「auc」フォルダを選択")
        config.set('Path', 'avi_utl_controller', folder_path)
        is_ok = bool(False)
    if not os.path.isabs(path.get('join_logo_scp')):
        config.set('Path', 'join_logo_scp', os.path.abspath(path.get('join_logo_scp')))
    if not os.path.isfile(path.get('join_logo_scp')):
        psl("「join_logo_scp」のパスが不正です(jlse_bat.bat)")
        select_type = [('jlse_bat.bat', '*.bat')]
        file_path = filedialog.askopenfilename(filetypes=select_type, initialdir=dir_path, title="「jlse_bat.bat」を選択")
        config.set('Path', 'join_logo_scp', file_path)
        is_ok = bool(False)
    if is_ok == bool(True):
        psl("パスのチェック完了。")
        save_config()
    else:
        path_check()


# ### 処理状況通知関係 ###
def notifire_encode_start(filename, count=1, total=1):
    if count == 0:
        message = "全" + str(total) + "ファイル処理開始"
        psl(message)
        if(total > 1) or (config.getboolean('Line', 'minimum')):
            line_notifire(message)
    else:
        message = str(count) + "/" + str(total) + "「" + filename + "」処理開始"
        psl(message)
        line_notifire(message)


def notifire_encode_end(count=1, total=1, start=DATE_TIME, end=DATE_TIME):
    if end == DATE_TIME:
        end = datetime.datetime.now()
    diff_s = p_time(start, end)
    if count == 0:
        message = "全" + str(total) + "ファイル処理完了（" + diff_s + "）"
        psl(message)
        if (total > 1) or (config.getboolean('Line', 'minimum')):
            line_notifire(message)
    else:
        message = str(count) + "/" + str(total) + "処理完了（" + diff_s + "）"
        psl(message)
        line_notifire(message)


# ### LINE通知関係 ###
def line_token_set(token):
    if len(token) > 2:
        config.set('Line', 'token', str(token))
        return line_notifire_test()


def line_notifire_test():
    psl('Lineテスト実行')
    status = line_notifire('test!テスト！', bool(True))
    if status[0] == bool(True):
        psl('Line通知成功-> 有効化します')
        config.set('Line', 'enable', str(bool(True)))
    else:
        psl('Line通知失敗-> 無効化します(トークンが正しいか確認してください)')
        config.set('Line', 'enable', str(bool(False)))
        # config.set('line', 'token', str()) # 消すと戻せなくなるので一応そのままにすることに
    save_config()
    return status


def line_notifire(message, test=bool(False)):
    if (test == bool(True)) or (config.getboolean('Line', 'enable') == bool(True)):
        line = config['Line']
        status = line_notifire_send(line.get('token'), message)
        if test == bool(False):
            if status[0] == bool(True):
                psl('Line通知しました(' + status[1] + ')')
            else:
                psl('Line通知は無効または失敗-> 通知テストします(' + status[1] + ')')
                line_notifire_test()
        return status


def line_notifire_send(token, message):
    payload = {
        'message': message
    }
    payload = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request('https://notify-api.line.me/api/notify', data=payload)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Authorization', 'Bearer ' + token)
    status = url_post(req)
    return status


def url_post(request):
    request.get_method = lambda: 'POST'
    http_ok = [bool(False), ""]
    try:
        with urllib.request.urlopen(request) as res:
            http_ok[1] = 'HTTP Response: ' + str(res.read())
            # psl(http_ok[1])
            http_ok[0] = bool(True)
    except urllib.error.HTTPError as e:
        config.set('Line', 'enable', str(bool(False)))
        http_ok[1] = 'HTTP Error: ' + str(e)
        # psl(http_ok[1])
    return http_ok


# ### 対象選択・パス変換 ###
def select_target_file(files_path=[], target_folder_path=""):
    if not target_folder_path == "":
        if os.path.isdir(target_folder_path) == bool(False):
            target_folder_path = ""
    if target_folder_path == "":
        target_folder_path = os.getcwd()
    select_type = [('*.ts, *.m2ts', '*.ts;*.m2ts')]
    select_file_path = [filedialog.askopenfilename(filetypes=select_type, initialdir=target_folder_path,
                        title="「変換対象ファイル(.ts .m2ts)」を選択")]
    psl("変換対象のファイルを選択: " + str(files_path + [select_file_path]))
    return files_path + [select_file_path]


def select_target_files(files_path=[], target_folder_path=""):
    if not target_folder_path == "":
        if os.path.isdir(target_folder_path) == bool(False):
            target_folder_path = ""
    if target_folder_path == "":
        target_folder_path = os.getcwd()
    select_type = [('*.ts, *.m2ts', '*.ts;*.m2ts')]
    select_files_path = filedialog.askopenfilenames(filetypes=select_type, initialdir=target_folder_path,
                                                    title="「変換対象ファイル(.ts .m2ts)」を選択")
    select_files_path = sorted(select_files_path, key=lambda p: p.split('/'[-1]))
    psl("変換対象のファイルを選択: " + str(files_path + select_files_path))
    return files_path + select_files_path


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
        psl("4." + str(change_path))
    # 元のパスから変更がある場合、表示しリネーム
    if not target_file_path == change_path:
        psl("ファイル名を変更： " + os.path.basename(change_path))
        os.rename(target_file_path, change_path)
    return change_path


def file_path2avs_path(target_file_path):
    if not os.path.isfile(target_file_path):
        psl("ファイルが見つかりません(file_path2avs_path: target_file_path)")
        psl("target: " + target_file_path)
        return ""
    avs_file_path = str(os.path.dirname(config['Path']['join_logo_scp']))
    avs_file_path += "/result"
    avs_file_path += "/" + str(os.path.splitext(os.path.basename(target_file_path))[0])
    avs_file_path += "/in_cutcm_logo.avs"
    if not os.path.isfile(avs_file_path):
        psl("ファイルが見つかりません(file_path2avs_path: avs_file_path)")
        psl("target: " + target_file_path)
        psl("avs: " + avs_file_path)
        return ""
    return avs_file_path


# ### JoinLogoSCP関係 ###
def run_join_logo_scp(target_file_path):
    psl("JoinLogoSCPによる処理開始")
    cmd_file = config['Path']['join_logo_scp']
    subprocess.run([cmd_file, target_file_path], encoding='cp932',
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    psl("処理終了")


# ### AviUtl Controller関係 ###
def run_avi_utl_controller(target_file_path):
    psl("AviUtlによるエンコード開始")
    mp4_filepath = os.path.dirname(target_file_path)
    # configのRename内mp4_filename_date_deleteがTrueの場合、年月日を確認し削除
    if config.getboolean('Rename', 'mp4_filename_date_delete') == bool(True):
        mp4_filename = os.path.basename(mp4_filepath)
        mp4_filename_tmp = mp4_filename
        pattern = r'\d{4}[年/]\d{1,2}[月/]\d{1,2}日?'
        res = re.findall(pattern, mp4_filename)
        if not res == []:
            mp4_filename = mp4_filename.replace(res[0], '')
            # 日付を削除したことにより、先頭の文字が下記になった場合、該当しなくなるまで削除
            pattern = ['-', '_', ' ']
            count = 0
            while count <= len(pattern):
                for pat in pattern:
                    if mp4_filename[0] == pat:
                        mp4_filename = mp4_filename[1:]
                        count = 0
                    else:
                        count += 1
            mp4_filepath = mp4_filepath[:-1*len(mp4_filename_tmp)] + mp4_filename
            psl(".mp4ファイル名から日付を削除しました。 : 「" + os.path.basename(mp4_filepath) + "」")
    mp4_filepath += ".mp4"
    exe_dir = config['Path']['avi_utl_controller']
    res = subprocess.run([exe_dir + "/auc_exec.exe", config['Path']['avi_utl']], encoding='cp932',
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    w_id = str(res.returncode)
    psl("WindowID: "+str(w_id))
    subprocess.run([exe_dir + "/auc_open.exe", w_id, target_file_path.replace('/', chr(ord('\\')))])
    subprocess.run([exe_dir + "/auc_plugout.exe", w_id, config['Auc']['enc_plugin_no'],
                    mp4_filepath.replace('/', chr(ord('\\')))])
    subprocess.run([exe_dir + "/auc_wait.exe", w_id])
    subprocess.run([exe_dir + "/auc_close.exe", w_id])
    subprocess.run([exe_dir + "/auc_exit.exe", w_id])
    psl("エンコード終了")


# ### 実行ルーティン関係 ###
def run_jlscp_auc(target_files_path, p_var, l_status):
    total = len(target_files_path)
    start_f = datetime.datetime.now()
    notifire_encode_start("", 0, total)
    p_count = 0
    if tk_enable:
        p_count = (total * 2 + 2)/100
        tk_progress_add(p_var, p_count)
        l_status.config(text="開始します...")
    for i, filepath in enumerate(target_files_path):
        filepath = file_rename(filepath)
        filename = os.path.splitext(os.path.basename(filepath))[0]
        if config.getboolean('Line', 'minimum') == bool(False):
            notifire_encode_start(filename, i+1, total)
        start = datetime.datetime.now()
        if tk_enable:
            tk_progress_add(p_var, p_count)
            l_status.config(text=str(i+1) + "/" + str(total) + " JLS処理中 「" + filename + "」")
        thr_jls = threading.Thread(target=run_join_logo_scp(filepath))
        thr_jls.start()
        avs_filepath = file_path2avs_path(filepath)
        if tk_enable:
            tk_progress_add(p_var, p_count)
            l_status.config(text=str(i+1) + "/" + str(total) + " AUC処理中 「" + filename + "」")
        if avs_filepath == "":
            psl("avsパスが不正のため、当該ファイルの処理を中断します")
        else:
            run_avi_utl_controller(avs_filepath)
        if config.getboolean('Line', 'minimum') == bool(False):
            notifire_encode_end(i+1, total, start)
    notifire_encode_end(0, total, start_f)
    if tk_enable:
        tk_progress_add(p_var, p_count)
        l_status.config(text="全" + str(total) + "処理完了")


def run_files_dialog_and_run_jlscp_auc():
    files_path = select_target_files()
    if not files_path == "":
        run_jlscp_auc(files_path, "", "")


# ### Tkinter関係 ###
def tk_listbox_list_insert(lf, string_list):
    for st in string_list:
        lf.insert(lf.size(), st)


def tk_filecount_update(count_label, files_list):
    count_label.config(text=str(len(files_list)) + "ファイル")


def tk_progress_add(progress_bar, int_val):
    progress_bar.set(progress_bar.get() + int_val)


def tk_progress_init(progress_bar):
    progress_bar.set(0)


def tk_line_token_window(tk_line_setting_button, l_status):
    global line_token
    l_status.config(text="Line Token設定")
    tkl_root = Tk()
    tkl_root.title('Lineのトークンを入力してください')
    # 文字入力欄
    tkl_frame = ttk.Frame(tkl_root, padding=(75, 2))
    tkl_frame.grid()
    tkl_label = ttk.Label(tkl_frame, text='Token', padding=(5, 2))
    tkl_label.grid(row=0, column=0, sticky=E)
    token = StringVar()
    # tkl_token_entry = ttk.Entry(tkl_frame, textvariable=token, width=75, show='*')
    tkl_token_entry = ttk.Entry(tkl_frame, textvariable=token, width=75)
    tkl_token_entry.grid(row=0, column=1)
    # OK、キャンセルボタン欄
    tkl_frame_b = ttk.Frame(tkl_frame, padding=(0, 5))
    tkl_frame_b.grid(row=2, column=1, sticky=W)
    tkl_button_ok = ttk.Button(tkl_frame_b,
                               text='OK',
                               command=lambda: tk_line_token_set(tkl_token_entry, tkl_button_ok,
                                                                 tk_line_setting_button, l_status))
    tkl_button_ok.pack(side=LEFT)
    tkl_button_close = ttk.Button(tkl_frame_b, text='閉じる', command=lambda: tkl_root.destroy())
    tkl_button_close.pack(side=LEFT)
    tkl_root.mainloop()


def tk_line_token_set(tkl_entry, tkl_button, tk_button_line, l_status):
    status = line_token_set(tkl_entry.get())
    if status[0]:
        tkl_entry.delete(0, END)
        tkl_entry.insert(0, "設定完了しました。閉じてください。")
        tkl_entry.configure(state='readonly')
        tkl_button.configure(state='disable')
        tk_button_line.configure(state='disable')
        l_status.config(text="Line Token設定完了")
    else:
        tkl_entry.delete(0, END)
        tkl_entry.insert(0, "テストに失敗しました。トークンを確認してください。")
        tkl_entry.configure(state='normal')


def tk_select_files(lf, l_status, l_count):
    l_status.config(text="ファイル選択")
    files = select_target_files()
    tk_listbox_list_insert(lf, files)
    tk_filecount_update(l_count, files)


def tk_files_list_select_clear(lf, l_status, l_count):
    l_status.config(text="選択項目をリストからクリア")
    if not lf.curselection() is None:
        filelist = list(lf.get(0, lf.size()-1))
        if len(filelist) > 1:
            for i, del_index in enumerate(lf.curselection()):
                del_path = filelist.pop(del_index-i)
                # print("del: " + str(del_index) + "|" + str(del_path))
                lf.delete(0, tkinter.END)
                tk_listbox_list_insert(lf, filelist)
        else:
            filelist = []
            lf.delete(0, tkinter.END)
        tk_filecount_update(l_count, filelist)

    
def tk_files_list_all_clear(lf, l_status, l_count):
    l_status.config(text="リストを全クリア")
    lf.delete(0, tkinter.END)
    tk_filecount_update(l_count, [])


def tk_run_jlscp_auc(lf, p_var, l_status):
    tk_progress_init(p_var)
    run_jlscp_auc(list(lf.get(0, tkinter.END)), p_var, l_status)


def tk_open_folder(folder_path=""):
    if folder_path == "":
        folder_path = str(os.path.dirname(config['Path']['join_logo_scp']))
        folder_path += "/result"
        folder_path = folder_path.replace('/', chr(ord('\\')))
    if not os.path.isabs(folder_path):
        folder_path = os.path.abspath(folder_path)
    folder_path += chr(ord('\\'))
    psl(folder_path)
    os.system('explorer.exe "%s"' % folder_path)


# ### メイン関係 ###
# Todo: tkinter コンフィグ表示
if __name__ == '__main__':
    config_check()
    path_check()
    # line_notifire_test()
    # ### 引数があるか確認
    argvs = sys.argv
    argc = len(argvs)
    if argc == 1:
        tk_enable = True
        # 宣言
        # Root宣言
        root = Tk()
        root.title('pyJoinLogoScpEncode')
        root.iconbitmap('inc_dir/icon.ico')
        # root.rowconfigure("all", minsize=30, weight=1)
        # root.columnconfigure("all", minsize=50, weight=1)
        root.geometry("800x800")
        # Status宣言
        frame_stat = tkinter.Frame(root)
        progress_var = tkinter.IntVar(frame_stat)
        progressbar = ttk.Progressbar(frame_stat, length=200, maximum=100, mode="determinate", variable=progress_var)
        label_status = ttk.Label(frame_stat, padding=2, justify="left", relief="sunken", text="初期化中...")
        label_filecount = ttk.Label(frame_stat, padding=2, justify="center", relief="sunken", text="0ファイル")
        # ListBox宣言
        frame_list = ttk.Frame(root)
        listbox_files = Listbox(frame_list, bd=2, justify="left", relief="solid", cursor="hand2", selectmode="extended")
        lf_scr_x = ttk.Scrollbar(frame_list, orient=HORIZONTAL, command=listbox_files.xview)
        listbox_files.configure(xscrollcommand=lf_scr_x.set)
        lf_scr_y = ttk.Scrollbar(frame_list, orient=VERTICAL, command=listbox_files.yview)
        listbox_files.configure(yscrollcommand=lf_scr_y.set)
        # Control宣言
        frame_ctrl = ttk.Frame(root)
        label_setting = ttk.Label(frame_ctrl, text='設定')
        button_line = ttk.Button(frame_ctrl, text='Line Token設定',
                                 command=lambda: tk_line_token_window(button_line, label_status))
        sep_setting_run = ttk.Separator(frame_ctrl, orient="horizontal")
        label_run = ttk.Label(frame_ctrl, text='ファイル選択・実行')
        button_select = ttk.Button(frame_ctrl, text='ファイル選択',
                                   command=lambda: tk_select_files(listbox_files, label_status, label_filecount))
        button_clear = ttk.Button(frame_ctrl, text='選択したファイルを除外',
                                  command=lambda: tk_files_list_select_clear(listbox_files, label_status,
                                                                             label_filecount))
        button_clear_all = ttk.Button(frame_ctrl, text='全ファイルを除外',
                                      command=lambda: tk_files_list_all_clear(listbox_files, label_status,
                                                                              label_filecount))
        button_run = ttk.Button(frame_ctrl, text='実行',
                                command=lambda: tk_run_jlscp_auc(listbox_files, progress_var, label_status))
        sep_run_open = ttk.Separator(frame_ctrl, orient="horizontal")
        label_open = ttk.Label(frame_ctrl, text='エクスプローラで表示')
        button_open_root = ttk.Button(frame_ctrl, text='プログラムフォルダ表示',
                                      command=lambda: tk_open_folder(os.getcwd()))
        button_open_result = ttk.Button(frame_ctrl, text='出力先フォルダ表示', command=lambda: tk_open_folder())

        # 配列＆表示
        # Root内配置
        frame_stat.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=1, pady=1)
        frame_ctrl.pack(side=tkinter.LEFT, fill=tkinter.Y, padx=10, pady=50)
        frame_list.pack(expand=True, side=tkinter.RIGHT, fill=tkinter.BOTH, padx=10, pady=10)
        # Status内配置
        label_filecount.pack(side=tkinter.RIGHT, padx=1)
        progressbar.pack(side=tkinter.LEFT, padx=1)
        label_status.pack(expand=True, side=tkinter.LEFT, fill=tkinter.X, padx=1)
        # List内配置
        lf_scr_x.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        lf_scr_y.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        listbox_files.pack(expand=True, side=tkinter.TOP, fill=tkinter.BOTH)
        # Control内配置
        set_ctrl_sep_pady = 10
        set_ctrl_button_pady = 5
        set_ctrl_button_ipady = 10
        label_setting.pack(pady=5)
        button_line.pack(fill=tkinter.X, pady=set_ctrl_button_pady, ipady=set_ctrl_button_ipady)
        sep_setting_run.pack(fill=tkinter.BOTH, padx=3, pady=set_ctrl_sep_pady)
        label_run.pack(pady=5)
        button_select.pack(fill=tkinter.X, pady=set_ctrl_button_pady, ipady=set_ctrl_button_ipady)
        button_clear.pack(fill=tkinter.X, pady=set_ctrl_button_pady, ipady=set_ctrl_button_ipady)
        button_clear_all.pack(fill=tkinter.X, pady=set_ctrl_button_pady, ipady=set_ctrl_button_ipady)
        button_run.pack(fill=tkinter.X, pady=set_ctrl_button_pady, ipady=set_ctrl_button_ipady)
        sep_run_open.pack(fill=tkinter.BOTH, padx=3, pady=set_ctrl_sep_pady, ipady=set_ctrl_button_ipady)
        label_open.pack(pady=5)
        button_open_root.pack(fill=tkinter.X, pady=set_ctrl_button_pady, ipady=set_ctrl_button_ipady)
        button_open_result.pack(fill=tkinter.X, pady=set_ctrl_button_pady, ipady=set_ctrl_button_ipady)

        # 表示判定
        if config.getboolean('Line', 'enable') == bool(True):
            button_line.configure(state='disable')

        root.mainloop()
    else:
        psl("引数あり")
        run_files_dialog_and_run_jlscp_auc()
