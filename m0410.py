import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from matplotlib.offsetbox import OffsetImage
import os
from datetime import datetime, timedelta


# 指定FFmpeg路径
plt.rcParams['animation.ffmpeg_path'] = 'C:\\py\\ffmpeg\\bin\\ffmpeg.exe'
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体

# 加载数据
data = pd.read_csv('c:\\Users\\yao\\Desktop\\342305616_ACTIVITY-record - clip.csv')

def cv(p):
    x,y,w,h=p
    return [x/screen_width,y/screen_height,w/screen_width,h/screen_height]
# 时间转换函数
def convert_time(timestamp):
    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt = datetime.strptime(timestamp, time_format) + timedelta(hours=8)
    return dt.strftime("%Y-%m-%d %H:%M:%S")
from datetime import datetime

def subtract_time(time1_str, time2_str):
    # 将时间字符串转换为 datetime 对象
    time_format = "%Y-%m-%d %H:%M:%S"
    time1 = datetime.strptime(time1_str, time_format)
    time2 = datetime.strptime(time2_str, time_format)
    
    # 计算时间差
    time_difference = time1 - time2
    
    # 提取时分秒部分
    hours, remainder = divmod(time_difference.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # 格式化为字符串
    return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

#print(subtract_time(time1, time2))  # 输出: 01:29:45

# 配速转换函数
def speed_to_pace(speed_mps):
    if speed_mps == 0:
        return "0"
    seconds_per_meter = 1 / speed_mps
    seconds_per_km = seconds_per_meter * 1000
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    pace_str = "{}\'{:02d}".format(minutes, seconds)
    return pace_str

# 创建一个figure对象
fig = plt.figure(figsize=(1920/100, 1080/100), facecolor='none')  # 设置figure的大小，并将背景设为透明
fig.patch.set_alpha(0)
#fig.patch.set_facecolor('lightyellow')

# 创建15个ax对象
num_axes = 6
colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightpink', 'lightcyan']  # 预定义的颜色列表

axes = []  # 用于存储所有的ax对象

# 屏幕宽度和高度
screen_width = 1920
screen_height = 1080
wlist=[
    [50,10,400,200], # 0 - 左1
    [440,10,200,200], # 1 - 左2
    [1920-410,10,400,200], # 2 - 左3
    [10,1080-500,600,480], # 3 - 地图
    [0,340,700,200], # 4 - pace
    [0,230,700,100]  # 5 - heart
    ]

for i in range(num_axes):
    # 随机选择一个颜色
    color = np.random.choice(colors)
    
    # 添加ax对象到figure中，并设置为半透明
    #ax = fig.add_axes(cv(wlist[i]), facecolor=color, alpha=0.5)
    ax = fig.add_axes(cv(wlist[i]), facecolor='none', alpha=0.5)
    ax.set_frame_on(False)
    ax.set_xticks([])  # 不显示x轴刻度
    ax.set_yticks([])  # 不显示y轴刻度
    #if i==4:
    #    #ax.set_ylim(min(data['speed2']) - 1, max(data['speed2']) + 1)
    #    ax.set_position([ax.get_position().x0, ax.get_position().y0, ax.get_position().width, 0.8])
#
    #if i==5:
    #    #ax.set_ylim(min(data['heart rate']) - 1, max(data['heart rate']) + 1)
    #    ax.set_position([ax.get_position().x0, ax.get_position().y0, ax.get_position().width, 0.8])

    
    axes.append(ax)

# 设置乌龟图像的文件夹路径
turtle_folder = 'turtle_frames'

# 获取乌龟图像文件夹中的所有图像文件
turtle_images = [os.path.join(turtle_folder, img) for img in os.listdir(turtle_folder) if img.endswith('.png')]

# 创建 OffsetImage 对象列表
turtle_img_objs = [OffsetImage(plt.imread(img), zoom=0.5) for img in turtle_images]

# 添加 OffsetImage 对象到画布上
turtle_ims = [None] * len(turtle_img_objs)

# 绘制地图函数
def plot_map(data,i):
    axes[3].clear()
    axes[3].scatter(data['position long'], data['position lat'], c='#ffff88', s=5)  # 绘制经纬度点
    #axes[3].set_xlim(x0,x1)  # 设置x轴范围
    #axes[3].set_ylim(y0,y1)  # 设置y轴范围
    axes[3].set_aspect('equal')  # 保持纵横比一致 否则地图会变形

    axes[4].clear()
    axes[4].scatter(range(len(data)),data['speed2'], c='#2D8CEB', s=1)  # 
    #axes[4].set_aspect('equal')  # 保持纵横比一致

    axes[5].clear()
    axes[5].scatter(range(len(data)),data['heart rate'], c='red', s=1)  # 
    #axes[5].set_aspect('equal')  # 保持纵横比一致

# 用于更新乌龟图像的函数
def update_turtle_image(ax, turtle_img_objs, turtle_ims, turtle_index):
    # 移除之前的乌龟图像对象
    if turtle_ims[turtle_index] is not None:
        turtle_ims[turtle_index].remove()
    
    # 添加新的乌龟图像对象
    turtle_im = ax.add_artist(turtle_img_objs[turtle_index])
    turtle_im.set_alpha(0)  # 设置透明度为0.5，范围为0到1之间    

    turtle_ims[turtle_index] = turtle_im

# 定义更新时间的函数
def update_time(i):
    print(i)
    time = convert_time(data['timestamp'][i])
    speed = speed_to_pace(data['enhanced speed'][i])
    speed2 = speed_to_pace(data['speed2'][i])
    heart_rate = int(data['heart rate'][i])
    cadence = int(data['cadence'][i] * 2)
    cadence2 = int(data['cadence2'][i] * 2)
    time_pass = subtract_time(time, convert_time(data['timestamp'][0])) #data['time_pass'][i]
    altitude = round(data['enhanced altitude'][i], 1)
    distance = round(data['distance'][i], 1)
    distance2 = round(data['distance2'][i], 1)
    j=0
    plot_map(data,i)
    for ax in axes:
        if j==0:
            ax.clear()  # 清空ax
            ax.text(0, 0.5, f"配速: {speed} DR {speed2}\n心率: {heart_rate}\n步频: {cadence} DR {cadence2}", fontsize=24, ha='left', va='center', color='#55CC66', transform=ax.transAxes)
        if j==1:
            ax.clear()  # 清空ax
            #ax.text(0, 0.5, str(i), ha='center', va='center', fontsize=12, color='black')
            # 计算应该显示的乌龟图像索引
            if float(data['speed2'][i])<3.52:
                turtle_index = (i) % 2 + 2
            else:
                turtle_index = (i) % 2 
            # 设置乌龟图像的位置（左上角）
            turtle_img_objs[0].set_offset((380, 50))
            turtle_img_objs[1].set_offset((380, 50))
            turtle_img_objs[2].set_offset((380, 50))
            turtle_img_objs[3].set_offset((380, 50))

            update_turtle_image(ax, turtle_img_objs, turtle_ims, turtle_index) 

        if j==2:
            ax.clear()  # 清空ax
            ax.text(0, 0.5, f"{time}\n用时: {time_pass}\n海拔: {altitude}\n距离: {distance} DR {distance2}", fontsize=24, ha='left', va='center', color='#55CC66', transform=ax.transAxes)
        if j==3:
            ax.scatter(data.loc[i, 'position long'], data.loc[i, 'position lat'], c='red', s=60)  # 绘制当前位置的大红点
        if j==4:
            ax.scatter(i, data.loc[i, 'speed2'], c='red', s=60)  # 绘制当前位置的大红点
        if j==5:
            ax.scatter(i, data.loc[i, 'heart rate'], c='red', s=60)  # 绘制当前位置的大红点

        #ax.set_frame_on(False)
        ax.set_xticks([])  # 不显示x轴刻度
        ax.set_yticks([])  # 不显示y轴刻度
        j=j+1


# 创建动画
ani = animation.FuncAnimation(fig, update_time, frames=len(data), interval=1000)

# 指定FFmpeg路径
plt.rcParams['animation.ffmpeg_path'] = 'C:\\py\\ffmpeg\\bin\\ffmpeg.exe'

# 保存动画为视频文件（QuickTime动画，支持alpha通道）
#ani.save('test20250003.mp4', writer='ffmpeg',  fps=1, dpi=100)

#plt.show()
# 保存动画为视频文件
#ani.save('running_overlay_yao_20240422v001.mp4', writer='ffmpeg', fps=1, dpi=100)
ani.save('running_overlay_yao_20240422v006.mov', writer='ffmpeg', fps=1, dpi=100, codec='png', bitrate=-1)
