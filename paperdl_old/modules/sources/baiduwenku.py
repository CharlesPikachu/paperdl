'''
Function:
    Seach and download papers from Baiduwenku
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import re
import json
import time
from .base import Base


'''Seach and download papers from Baiduwenku'''
class Baiduwenku(Base):
    def __init__(self, config=None, logger_handle=None, **kwargs):
        super(Baiduwenku, self).__init__(config, logger_handle, **kwargs)
        self.source = 'baiduwenku'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        }
    '''parse paper infos before dowload paper'''
    def parseinfosbeforedownload(self, paperinfos):
        for paperinfo in paperinfos:
            self.parseinfobeforedownload(paperinfo)
            paperinfo['source'] = self.source
        return paperinfos
    '''parse paper info before dowload paper'''
    def parseinfobeforedownload(self, paperinfo):
        # prepare
        input_content = paperinfo['input']
        url = input_content.split('?')[0] + '?edtMode=2'
        headers = self.headers.copy()
        if 'cookie' in paperinfo: headers['Cookie'] = paperinfo['cookie']
        headers['Referer'] = url
        self.session.headers.update(headers)
        # obtain the basic infos
        response = self.session.get(url)
        page_data = re.search( r'var pageData = (.*);', response.text)
        page_data = json.loads(page_data.group(1))
        title = re.search( r'<title>(.*) - 百度文库</title>', response.text).group(1)
        filetype = page_data['viewBiz']['docInfo']['fileType']
        docid = url.split('?')[0].split('/')[-1][:-5]
        paperinfo['savename'] = title
        paperinfo['filetype'] = filetype
        paperinfo['docid'] = docid
        # ppt
        if page_data['readerInfo']['tplKey'] == 'new_view' and filetype in ['ppt']:
            download_url = page_data['readerInfo']['htmlUrls']
            paperinfo['download_url'] = download_url
        # word, pdf, excel
        elif page_data['readerInfo']['tplKey'] == 'html_view' and filetype in ['word', 'pdf', 'excel']:
            jsons = {x['pageIndex']: x['pageLoadUrl'] for x in page_data['readerInfo']['htmlUrls']['json']}
            pngs = {x['pageIndex']: x['pageLoadUrl'] for x in page_data['readerInfo']['htmlUrls']['png']}
            fonts_csss = {x['pageIndex']: 'https://wkretype.bdimg.com/retype/pipe/' + docid + '?pn=' + str(x['pageIndex']) + '&t=ttf&rn=1&v=6' + x['param'] for x in page_data['readerInfo']['htmlUrls']['ttf']}
            if page_data['readerInfo']['page'] > 100:
                for pn in list(range(101, data['readerInfo']['page'] + 1, 50)):
                    url = f"https://wenku.baidu.com/ndocview/readerinfo?doc_id={docid}&docId={docid}&type=html&clientType=1&pn={pn}&t={str(int(time.time()))}&isFromBdSearch=0&rn=50"
                    response = self.session.get(url)
                    page_data_others = json.loads(response.text)['data']['htmlUrls']
                    jsons.update({x['pageIndex']: x['pageLoadUrl'] for x in page_data_others['json']})
                    pngs.update({x['pageIndex']: x['pageLoadUrl'] for x in page_data_others['png']})
                    fonts_csss.update({x['pageIndex']: 'https://wkretype.bdimg.com/retype/pipe/' + docid + '?pn=' + str(x['pageIndex']) + '&t=ttf&rn=1&v=6' + x['param'] for x in data_temp['ttf']})
            download_url = {'fonts_csss': fonts_csss, 'jsons': jsons, 'pngs': pngs}
            paperinfo['download_url'] = download_url
        # text
        elif page_data['readerInfo']['tplKey'] == 'txt_view' and filetype in ['txt']:
            lines = re.findall(r'<p class="p-txt">(.*)</p>', response.text)
            lines = [line for line in lines if line]
            lines[-1] = lines[-1][:-1]
            download_url = 'https://wkretype.bdimg.com/retype/text/' + docid + page_data['readerInfo']['md5sum'] + '&pn=2&rn=' + str(int(page_data['viewBiz']['docInfo']['page']) - 1) + '&type=txt&rsign=' + page_data['readerInfo']['rsign'] + '&callback=cb&_=' + str(int(time.time()))
            response = self.session.get(download_url)
            lines_others_json = json.loads(response.text[3: -1])
            lines_others = [x['parags'][0]['c'][:-2] for x in lines_others_json]
            lines = lines + lines_others
            paperinfo['download_url'] = download_url
            paperinfo['lines'] = lines
            paperinfo['ext'] = 'txt'