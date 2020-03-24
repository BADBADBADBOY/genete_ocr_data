from lxml.etree import Element, SubElement, tostring
from utils import log
import shutil
import os
import cv2
import numpy as np

def get_pic_dir(out_put_dir):
    img_dir = os.path.join(out_put_dir, "img")
    return img_dir


def get_data_dir(out_put_dir):
    data_dir = os.path.join(out_put_dir, "json")
    return data_dir

def get_label_dir(out_put_dir):
    data_dir = os.path.join(out_put_dir, "txt")
    return data_dir

def get_voc_data_dir(out_put_dir):
    voc_data = os.path.join(out_put_dir, "voc_data")
    return voc_data

def get_show_data_dir(out_put_dir):
    show_data = os.path.join(out_put_dir, "show_result")
    return show_data

def gen_all_pic():
    """
    生成全部图片
    :return:
    """
    from service import conf
    gen_count = conf['base']['count_per_process']

    index = 0
    while index < gen_count:
        log.info("-" * 20 + " generate new picture {index}/{gen_count}".format(index=index,gen_count=gen_count) + "-" * 20)
        dump_data = gen_pic()
        if dump_data:
            gen_label_data(dump_data)
            show_data(dump_data)
            # 生成voc
            if conf['base']['gen_voc']:
                gen_voc(dump_data)
            index += 1


def gen_pic():
    from service import layout_provider
    layout = layout_provider.gen_next_layout()

    if not layout.is_empty():
        dump_data = layout.dump()
        return dump_data
    else:
        log.info("-" * 10 + "layout is empty" + "-" * 10)
        return None

    
def gen_label_data(layout_data):
    # 得到icdar样式的label文本
    from service import conf
    out_put_dir = conf['provider']['layout']['out_put_dir']
    shutil.rmtree(os.path.join(out_put_dir,'text_img'))
    shutil.rmtree(os.path.join(out_put_dir,'text_img_info'))
    label_data_dir = get_label_dir(out_put_dir=out_put_dir)
    os.makedirs(label_data_dir, exist_ok=True)
    fid = open(os.path.join(label_data_dir,layout_data['pic_name'][:-4]+'.txt'),'w+',encoding='utf-8')
    for item in layout_data['fragment']:
        coord = np.array(item['coord']).reshape(4,2)
        bbox = item['box']
        coord[:,0] = coord[:,0] + bbox[0]
        coord[:,1] = coord[:,1] + bbox[1]
        coord = coord.reshape(8).tolist()
        coord = ','.join([str(x) for x in coord ])
        label = item['data']
        fid.write(coord+','+label+'\n')
    fid.close()
    log.info("get label data success!")
    
def show_data(layout_data):
    """
    显示检测文本框
    :return:
    """
    from service import conf
    out_put_dir = conf['provider']['layout']['out_put_dir']
    is_show =  conf['base']['is_show']
    if(is_show is True):
        show_data_dir = get_show_data_dir(out_put_dir=out_put_dir)
        os.makedirs(show_data_dir, exist_ok=True)
        img_dir = get_pic_dir(out_put_dir)
        img = cv2.imread(os.path.join(img_dir,layout_data['pic_name']))
        for item in layout_data['fragment']:
            coord = np.array(item['coord']).reshape(4,2)
            bbox = item['box']
            coord[:,0] = coord[:,0] + bbox[0]
            coord[:,1] = coord[:,1] + bbox[1]
            coord = coord.reshape(8).tolist()
    #         img = cv2.rectangle(img,(bbox[0],bbox[1]),(bbox[2],bbox[3]),(255,0,0),2)
            img = cv2.line(img,(coord[0],coord[1]),(coord[2],coord[3]),(0,0,255),1)
            img = cv2.line(img,(coord[2],coord[3]),(coord[4],coord[5]),(0,0,255),1)
            img = cv2.line(img,(coord[4],coord[5]),(coord[6],coord[7]),(0,0,255),1)
            img = cv2.line(img,(coord[6],coord[7]),(coord[0],coord[1]),(0,0,255),1)
        cv2.imwrite(os.path.join(show_data_dir,layout_data['pic_name']),img)

   
    log.info("get show data success!")


def gen_voc(layout_data):
    """
    生成voc数据集
    :return:
    """
    from service import conf
    out_put_dir = conf['provider']['layout']['out_put_dir']
    voc_data_dir = get_voc_data_dir(out_put_dir=out_put_dir)

    voc_img_dir = os.path.join(voc_data_dir, "voc_img")
    voc_xml_dir = os.path.join(voc_data_dir, "voc_xml")
    os.makedirs(voc_img_dir, exist_ok=True)
    os.makedirs(voc_xml_dir, exist_ok=True)

    pic_dir = get_pic_dir(out_put_dir)
    pic_name = layout_data['pic_name']
    pic_path = os.path.join(pic_dir, pic_name)
    pic_save_to_path = os.path.join(voc_img_dir, pic_name)

    # 拷贝图片
    shutil.copy(pic_path, pic_save_to_path)
    log.info("copy img success")

    # 生成标签文本
    _gen_voc(voc_xml_dir, data=layout_data)

    log.info("voc data gen success")


def _gen_voc(save_dir, data, image_format='jpg'):
    w = data['width']
    h = data['height']

    node_root = Element('annotation')
    '''folder'''
    node_folder = SubElement(node_root, 'folder')
    node_folder.text = 'JPEGImages'
    '''filename'''
    node_filename = SubElement(node_root, 'filename')
    node_filename.text = data['pic_name']
    '''source'''
    node_source = SubElement(node_root, 'source')
    node_database = SubElement(node_source, 'database')
    node_database.text = 'The VOC2007 Database'
    node_annotation = SubElement(node_source, 'annotation')
    node_annotation.text = 'PASCAL VOC2007'
    node_image = SubElement(node_source, 'image')
    node_image.text = 'flickr'
    '''size'''
    node_size = SubElement(node_root, 'size')
    node_width = SubElement(node_size, 'width')
    node_width.text = str(w)
    node_height = SubElement(node_size, 'height')
    node_height.text = str(h)
    node_depth = SubElement(node_size, 'depth')
    node_depth.text = '3'
    '''segmented'''
    node_segmented = SubElement(node_root, 'segmented')
    node_segmented.text = '0'
    '''object coord and label'''
    for i, fragment in enumerate(data['fragment']):
        node_object = SubElement(node_root, 'object')
        node_name = SubElement(node_object, 'name')
        node_name.text = fragment['orientation'][0] + "_text"
        node_truncated = SubElement(node_object, 'truncated')
        node_truncated.text = '0'
        node_difficult = SubElement(node_object, 'difficult')
        node_difficult.text = '0'
        node_bndbox = SubElement(node_object, 'bndbox')
        node_xmin = SubElement(node_bndbox, 'xmin')
        node_xmin.text = str(fragment['box'][0])
        node_ymin = SubElement(node_bndbox, 'ymin')
        node_ymin.text = str(fragment['box'][1])
        node_xmax = SubElement(node_bndbox, 'xmax')
        node_xmax.text = str(fragment['box'][2])
        node_ymax = SubElement(node_bndbox, 'ymax')
        node_ymax.text = str(fragment['box'][3])

    xml = tostring(node_root, pretty_print=True)  # 格式化显示，该换行的换行

    save_xml = os.path.join(save_dir, data['pic_name'].replace(image_format, 'xml'))
    with open(save_xml, 'wb') as f:
        f.write(xml)
