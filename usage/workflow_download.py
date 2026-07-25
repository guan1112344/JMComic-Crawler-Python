from jmcomic import *
import os
from jmcomic.cl import JmcomicUI


# ä¸æ¹å¡«å¥ä½ è¦ä¸è½½çæ¬å­çidï¼ä¸è¡ä¸ä¸ªï¼æ¯è¡çé¦å°¾å¯ä»¥æç©ºç½å­ç¬¦
jm_albums = '''
1212672
1446079
626220
139078
142464
113148
496153
410272
1200544
291210
506940
580020
544353
366520
501663
378194
1114796
468017
208514
1168908
1025341
599349
602517
520192
598997
1160395
377532
1215085
181739
246117
454127
616250
368640
552848
144132
218796
1068594
480713
364547
340776
421058
372619
389479
530571
500946
544851
334721
1084698
298716
1228261
1229285
1229287
1229377
558396
393748
612827
584491
423192
182024
604673
1204270
646675
1062978
1226410
233696
485117
1182984
427111
1224351
414386
445539
469239
468649
1164988
1208626
1211693
497729
608652
1193833
382591
486760
287395
226080
306404
372880
1149620
258344
467180
180491
1192423
553496
482932
9013
20833
36580
95952
95951
89107
95949
100379
104634
114159
114397
124174
259639
299987
301405
409657
477258
436283
502013
515192
483831
517163
516638
534074
546580
584448
1225104
349244
278406
276039
607505
225914
2830
23022
37768
51721
53185
165804
179163
180045
181318
185208
187793
187809
205429
209654
214180
213852
218269
289824
392085
424022
448087
449353
476050
487705
507975
178386
222286
224346
225604
230657
230029
228449
230433
233988
234544
239642
236741
248167
248170
257189
527941
260652
516102
638494
1023747
1054804
1054220
1227290
569085
568429
581079
304538
317727
135
330028
342295
250078
378942
386273
403508
404137
445881
433665
584566
597511
626343
641438
647781
642951
651738
1016577
1018910
1021427
1023592
1053618
1027131
1026658
1038310
1038319
1049919
1067523
1081549
1142102
1133898
1168982
1185936
1191522
1194290
1196806
1197438
1200179
1201989
1202709
1205278
1214544
1215962
1215408
1197182
1220227
1192427
324072
1062501
1195597
613905
1205191
349621
505963
1169705
499858
235692
1113207
498750
1095496
1061314
1074744
612896
147914
575789
265863
1128122
526216
1059005
122916
1059251
1078526
646443
1069514
1052923
1065812
1049368
1046194
205512
1029277
1035108
247045
346840
398668
334858
149573
303892
1021964
572167
224412
1032498
1038949
1017030
1037449
650291
1026827
1254368
1156509
1454522

1451059
1453339
1453318
1443931
1444097
'''

# åç¬ä¸è½½ç« è
jm_photos = '''
'''

def env(name, default, trim=('[]', '"')):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default
    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]
    return value


def get_id_set(env_name, given):
    aid_set = set()
    for text in [
        given,
        (env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))
    return aid_set


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS', jm_albums)
    photo_id_set = get_id_set('JM_PHOTO_IDS', jm_photos)

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')


def get_option():
    # è¯»å option éç½®æä»¶
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_workflow_download.yml')))

    # æ¯æå·¥ä½æµè¦çéç½®æä»¶çéç½®
    cover_option_config(option)

    # æè¯·æ±éè¯¯çhtmlä¸è½½å°æä»¶ï¼æ¹ä¾¿GitHub Actionsä¸è½½æ¥çæ¥å¿
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(env('DIR_RULE', 'Bd_Analyze'), base_dir=os.environ.get('JM_DOWNLOAD_DIR', '.'))
        option.dir_rule = the_new

    impl = env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)

    pdf_option = env('PDF_OPTION', None)
    if pdf_option and pdf_option != 'å¦':
        call_when = 'after_album' if pdf_option == 'æ¯ | æ¬å­ç»´åº¦åå¹¶pdf' else 'after_photo'
        plugin = [{
            'plugin': Img2pdfPlugin.plugin_key,
            'kwargs': {
                'pdf_dir': option.dir_rule.base_dir + '/pdf/',
                'filename_rule': call_when[6].upper() + 'id',
                'delete_original_file': True,
            }
        }]
        option.plugins[call_when] = plugin


def log_before_raise():
    jm_download_dir = env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    def decide_filepath(e):
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)
        if resp is None:
            suffix = str(time_stamp())
        else:
            suffix = resp.url
        name = '-'.join(
            fix_windir_name(it)
            for it in [
                e.description,
                current_thread().name,
                suffix
            ]
        )
        path = f'{jm_download_dir}/ãåºéäºã{name}.log'
        return path

    def exception_listener(e: JmcomicException):
        """
 å¼å¸¸çå¬å¨ï¼å®ç°äºå¨ GitHub Actions ä¸ï¼æè¯·æ±éè¯¯çä¿¡æ¯ä¸è½½å°æä»¶ï¼æ¹ä¾¿è°è¯åéç¥ä½¿ç¨è
 """
        # å³å®è¦åå¥çæä»¶è·¯å¾
        path = decide_filepath(e)

        # åå¤åå®¹
        content = [
            str(type(e)),
            e.msg,
        ]
        for k, v in e.context.items():
            content.append(f'{k}: {v}')

        # resp.text
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)
        if resp:
            content.append(f'ååºææ¬: {resp.text}')

        # åæä»¶
        write_text(path, '\n'.join(content))


    JmModuleConfig.register_exception_listener(JmcomicException, exception_listener)


if __name__ == '__main__':
    main()

