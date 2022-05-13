'''
Function:
    Downloader
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import os
import re
import json
import shutil
import base64
import requests
from alive_progress import alive_bar
from .misc import touchdir, filterBadCharacter


'''Downloader'''
class Downloader():
    def __init__(self, paperinfo, session=None, **kwargs):
        self.paperinfo = paperinfo
        self.session = requests.Session() if session is None else session
        self.__setheaders(paperinfo['source'])
    '''start to download according to paperinfo'''
    def start(self):
        paperinfo, session, headers = self.paperinfo, self.session, self.headers
        if not paperinfo['download_url']: return False
        paperinfo['savename'] = filterBadCharacter(paperinfo['savename'])
        touchdir(paperinfo['savedir'])
        if paperinfo['source'] in ['baiduwenku']: return self.downloadfrombaiduwenku()
        with session.get(paperinfo['download_url'], headers=headers, stream=True) as response:
            if response.status_code not in [200]: return False
            total_size, chunk_size, downloaded_size = int(response.headers['content-length']), paperinfo.get('chunk_size', 1024), 0
            savepath = os.path.join(paperinfo['savedir'], f"{paperinfo['savename']}.{paperinfo['ext']}")
            text, fp = '[FileSize]: %0.2fMB/%0.2fMB', open(savepath, 'wb')
            with alive_bar(manual=True) as bar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if not chunk: continue
                    fp.write(chunk)
                    downloaded_size += chunk_size
                    bar.text(text % (downloaded_size / 1024 / 1024, total_size / 1024 / 1024))
                    bar(min(downloaded_size / total_size, 1))
        return True
    '''download from baiduwenku'''
    def downloadfrombaiduwenku(self):
        paperinfo, session = self.paperinfo, self.session
        touchdir(paperinfo['docid'])
        if paperinfo['filetype'] in ['ppt']:
            text = '[PageSize]: %d/%d'
            with alive_bar(manual=True) as bar:
                for idx, download_url in enumerate(paperinfo['download_url']):
                    fp = open(os.path.join(paperinfo['docid'], f'{idx}.jpg'), 'wb')
                    fp.write(session.get(download_url).content)
                    fp.close()
                    bar.text(text % (idx+1, len(paperinfo['download_url'])))
                    bar(min((idx + 1) / len(paperinfo['download_url']), 1))
            imagepaths = [os.path.join(paperinfo['docid'], f'{idx}.jpg') for idx in range(len(paperinfo['download_url']))]
            import img2pdf
            with open(os.path.join(paperinfo['savedir'], f"{paperinfo['savename']}.{paperinfo['ext']}"), 'wb') as fp:
                fp.write(img2pdf.convert(imagepaths))
            shutil.rmtree(paperinfo['docid'])
            return True
        elif paperinfo['filetype'] in ['word', 'pdf', 'excel']:
            text = '[PageSize-Fonts]: %d/%d'
            with alive_bar(manual=True) as bar:
                for idx, _ in enumerate(range(len(paperinfo['download_url']['fonts_csss']))):
                    download_url = paperinfo['download_url']['fonts_csss'][idx+1]
                    response = session.get(download_url)
                    fonts = re.findall(r'@font-face {src: url\(data:font/opentype;base64,(.*?)\)format\(\'truetype\'\);font-family: \'(.*?)\';', response.text)
                    for font in fonts:
                        fp = open(os.path.join(paperinfo['docid'], f'{font[1]}.ttf'), 'wb')
                        fp.write(base64.b64decode(font[0]))
                        fp.close()
                    bar.text(text % (idx+1, len(paperinfo['download_url']['fonts_csss'])))
                    bar(min((idx + 1) / len(paperinfo['download_url']['fonts_csss']), 1))
            text, jsons = '[PageSize-Jsons]: %d/%d', []
            with alive_bar(manual=True) as bar:
                for idx, _ in enumerate(range(len(paperinfo['download_url']['jsons']))):
                    download_url = paperinfo['download_url']['jsons'][idx+1]
                    response = session.get(download_url)
                    jsons.append(json.loads(re.search(r'wenku_[0-9]+\((.*)\)', response.text).group(1)))
                    bar.text(text % (idx+1, len(paperinfo['download_url']['jsons'])))
                    bar(min((idx + 1) / len(paperinfo['download_url']['jsons']), 1))
            text = '[PageSize-Pngs]: %d/%d'
            with alive_bar(manual=True) as bar:
                for idx, _ in enumerate(range(len(paperinfo['download_url']['jsons']))):
                    try:
                        download_url = paperinfo['download_url']['pngs'][idx+1]
                        response = session.get(download_url)
                        fp = open(os.path.join(paperinfo['docid'], f'{idx+1}.png'), 'wb')
                        fp.write(response.content)
                    except:
                        pass
                    bar.text(text % (idx+1, len(paperinfo['download_url']['jsons'])))
                    bar(min((idx + 1) / len(paperinfo['download_url']['jsons']), 1))
            text = '[PageSize-Generate]: %d/%d'
            with alive_bar(manual=True) as bar:
                for idx, _ in enumerate(range(len(paperinfo['download_url']['jsons']))):
                    self.savepdfforbaiduwenku(paperinfo['docid'], idx+1, jsons[idx])
                    bar.text(text % (idx+1, len(paperinfo['download_url']['jsons'])))
                    bar(min((idx + 1) / len(paperinfo['download_url']['jsons']), 1))
            text = '[PageSize-Merge]: %d/%d'
            pdfs = {x[:-4]: os.path.join(paperinfo['docid'], x) for x in os.listdir(paperinfo['docid']) if x[-4:] == '.pdf'}
            from PyPDF2 import PdfFileMerger, PdfFileReader
            file_merger = PdfFileMerger()
            with alive_bar(manual=True) as bar:
                for idx, _ in enumerate(range(len(paperinfo['download_url']['jsons']))):
                    with open(pdfs[str(idx + 1)], 'rb') as fp:
                        file_merger.append(PdfFileReader(fp))
                    bar.text(text % (idx+1, len(paperinfo['download_url']['jsons'])))
                    bar(min((idx + 1) / len(paperinfo['download_url']['jsons']), 1))
            file_merger.write(os.path.join(paperinfo['savedir'], f"{paperinfo['savename']}.{paperinfo['ext']}"))
            shutil.rmtree(paperinfo['docid'])
            return True
        elif paperinfo['filetype'] in ['txt']:
            text, fp = '[PageSize]: %d/%d', open(os.path.join(paperinfo['savedir'], f"{paperinfo['savename']}.{paperinfo['ext']}"), 'w')
            with alive_bar(manual=True) as bar:
                for idx, line in enumerate(paperinfo['lines']):
                    fp.write(line)
                    bar.text(text % (idx+1, len(paperinfo['lines'])))
                    bar(min((idx + 1) / len(paperinfo['lines']), 1))
            return True
        else:
            return False
    '''save pdf for baiduwenku'''
    def savepdfforbaiduwenku(self, docid, pagenum, data):
        from PIL import Image
        from imp import reload
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        canvas_pdf = canvas.Canvas(
            os.path.join(docid, f'{pagenum}.pdf'),
            pagesize=(data['page']['pw'], data['page']['ph']),
        )
        styles = dict()
        for style in data['style']:
            for style_c in style['c']:
                if not styles.get(style_c):
                    styles[style_c] = dict()
                for style_s in style['s']:
                    styles[style_c][style_s] = style['s'][style_s]
        ttfs = [x for x in os.listdir(docid) if x[-4:] == '.ttf' and int(x[-8: -4], 16) == pagenum]
        reload(pdfmetrics)
        for ttf in ttfs:
            pdfmetrics.registerFont(TTFont(ttf[:-4], os.path.join(docid, ttf)))
        try: image = Image.open(os.path.join(docid, f'{pagenum}.png'))
        except: image = None
        touchdir(os.path.join(docid, str(pagenum)))
        data_body = sorted(data['body'], key=lambda item: item['p']['z'])
        for item in data_body:
            if item['t'] == 'word':
                style = dict()
                if item.get('r'):
                    for item_r in item['r']: style.update(styles[item_r])
                if item.get('s'): style.update(item['s'])
                textobject = canvas_pdf.beginText()
                textobject.setTextOrigin(
                    item['p']['x'],
                    data['page']['ph'] - item['p']['y'] - 14
                )
                if style.get('font-family'):
                    textobject.setFont(
                        style['font-family'], 
                        float(style['font-size']) if style.get('font-size') else 16
                    )
                if style.get('letter-spacing'):
                    textobject.setCharSpace(float(style['letter-spacing']))
                if style.get('color'):
                    textobject.setFillColorRGB(
                        int(style['color'][1: 3], 16) / 255,
                        int(style['color'][3: 5], 16) / 255,
                        int(style['color'][5: 7], 16) / 255
                    )
                textobject.setFillColorRGB(0, 0, 0)
                textobject.textLine(item['c'])
                canvas_pdf.drawText(textobject)
            elif item['t'] == 'pic':
                if item['ps'] and item['ps'].get('_drop') and item['ps'].get('_drop') == 1:
                    continue
                if image is None:
                    continue
                image_crop = image.crop((
                    int(item['c']['ix']), 
                    int(item['c']['iy']),
                    int(item['c']['iw'] + item['c']['ix']), 
                    int(item['c']['ih'] + item['c']['iy'])
                ))
                image_width, image_height = (None, None)
                if int(item['c']['iw']) != int(item['p']['w']) or int(item['c']['ih']) != int(item['p']['h']):
                    image_width, image_height = item['p']['w'], item['c']['ih'] / item['c']['iw'] * item['p']['w']
                image_crop.save(os.path.join(docid, str(pagenum), '{}-{}.png'.format(item['p']['x'], item['p']['y'])))
                canvas_pdf.drawImage(
                    os.path.join(docid, str(pagenum), '{}-{}.png'.format(item['p']['x'], item['p']['y'])), 
                    int(item['p']['x']), 
                    data['page']['ph'] - int(item['p']['y']) - image_height if image_height else int(item['c']['ih']), 
                    width=image_width,
                    height=image_height,
                    mask='auto'
                )
        canvas_pdf.showPage()
        canvas_pdf.save()
    '''set request headers'''
    def __setheaders(self, source):
        if hasattr(self, f'{source}_headers'):
            self.headers = getattr(self, f'{source}_headers')
        else:
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
            }