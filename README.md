# Text data generate

- generate ocr dataset, text detection, text recognize dataset generate.
用来生成ocr数据，文字检测数据，文字识别

## 实现的功能：

- 生成基于不同语料的，不同字体、字号、颜色、旋转角度的文字贴图
- 支持多进程快速生成
- 文字贴图按照指定的布局模式填充到布局块中
- 在图像中寻找平滑区域当作布局块
- 支持文字区域的图块抠取导出（导出json文件，txt文件和图片文件，可生成voc数据,icdar2015格式数据）
- 支持用户自己配置各项生成配(图像读取，生成路径，各种概率)

## 效果预览

### 生成图片示例:

![](./output/show_result/1.jpg)
![](./output/show_result/2.jpg)
![](./output/show_result/3.jpg)



### 使用方式

- 环境安装(Python3.6+，建议使用conda环境)    
    ```
    # step 1
    pip install requirements.txt
    # step 2
    sh make.sh
    ```
  
- 编辑配置文件`config.yml`（可选）
    
- 执行生成脚本

    ```
    python3 run.py
    ```
  
- 生成的数据
    
    生成的数据存放在`config.yml`中的`provider> layout> out_put_dir`指定的目录下。
	
	
     
#### 本项目修改自TextGenerator，因为该项目暂不支持四角点，所以就自己动手了
原项目地址：https://github.com/BboyHanat/TextGenerator