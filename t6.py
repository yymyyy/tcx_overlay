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
data = pd.read_csv('act.csv')

# 时间转换函数
def convert_time(timestamp):
    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt = datetime.strptime(timestamp, time_format) + timedelta(hours=8)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

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

# 创建画布
fig, ax = plt.subplots(figsize=(1920/100, 1080/100), tight_layout=True)
fig.patch.set_facecolor('lightyellow')
ax.spines['bottom'].set_color('lightyellow')  # 设置底部边框颜色为红色
ax.spines['top'].set_color('lightyellow')     # 设置顶部边框颜色为红色
ax.spines['left'].set_color('lightyellow')    # 设置左侧边框颜色为红色
ax.spines['right'].set_color('lightyellow')   # 设置右侧边框颜色为红色
ax.tick_params(axis='x', colors='lightyellow')  # 设置x轴文字颜色为紫色
ax.tick_params(axis='y', colors='lightyellow')  # 设置y轴文字颜色为紫色
ax.xaxis.get_major_ticks()[-1].label1.set_color('lightyellow')
ax.yaxis.get_major_ticks()[-1].label1.set_color('lightyellow')
fig.set_size_inches(1920/100, 1080/100)
ax.set_frame_on(False)
ax.axis('off') 
ax.set_xticks([])
ax.set_yticks([])

# 设置乌龟图像的文件夹路径
turtle_folder = 'turtle_frames'

# 获取乌龟图像文件夹中的所有图像文件
turtle_images = [os.path.join(turtle_folder, img) for img in os.listdir(turtle_folder) if img.endswith('.png')]

# 创建 OffsetImage 对象列表
turtle_img_objs = [OffsetImage(plt.imread(img), zoom=0.5) for img in turtle_images]

# 添加 OffsetImage 对象到画布上
turtle_ims = [None] * len(turtle_img_objs)


# 绘制地图函数
def plot_map(data):
    ax.clear()
    ax.scatter(data['longitude'], data['latitude'], c='blue', s=10)  # 绘制经纬度点
    deltax=data['longitude'].max()-data['longitude'].min()
    deltay=data['latitude'].max()-data['latitude'].min()
    x0=data['longitude'].min()-deltax*0.1
    x1=data['longitude'].max()+deltax*2
    y0=data['latitude'].min()-deltay*7
    y1=data['latitude'].max()+deltay*0.5
    ax.set_xlim(x0,x1)  # 设置x轴范围
    ax.set_ylim(y0,y1)  # 设置y轴范围
    ax.set_aspect('equal')  # 保持纵横比一致


# 用于更新乌龟图像的函数
def update_turtle_image(ax, turtle_img_objs, turtle_ims, turtle_index):
    # 移除之前的乌龟图像对象
    if turtle_ims[turtle_index] is not None:
        turtle_ims[turtle_index].remove()
    
    # 添加新的乌龟图像对象
    turtle_im = ax.add_artist(turtle_img_objs[turtle_index])
    turtle_im.set_alpha(0)  # 设置透明度为0.5，范围为0到1之间    

    turtle_ims[turtle_index] = turtle_im

# 更新函数，用于在每一帧更新文本内容和动画效果
def update_map(i):
    print(i)
    plot_map(data)
    ax.scatter(data.loc[i, 'longitude'], data.loc[i, 'latitude'], c='red', s=100)  # 绘制当前位置的大红点

    time = convert_time(data['time'][i])
    speed = speed_to_pace(data['speed'][i])
    heart_rate = data['heart_rate'][i]
    cadence = data['cadence'][i] * 2
    time_pass = data['time_pass'][i]
    altitude = round(data['altitude'][i], 1)
    distance = round(data['distance'][i], 1)
    
    ax.text(0.05, 0.05, f"配速: {speed}\n心率: {heart_rate}\n步频: {cadence}", fontsize=24, ha='left', va='bottom', color='green', transform=ax.transAxes)
    ax.text(0.95, 0.05, f"{time}\n用时: {time_pass}\n海拔: {altitude}\n距离: {distance}", fontsize=24, ha='right', va='bottom', color='green', transform=ax.transAxes)

    # 指定图像显示的位置和大小（例如X轴的25%位置，Y轴的30%位置，图像大小为原始图像大小的一半）

    # 计算应该显示的乌龟图像索引
    if float(data['speed'][i])<3.52:
        turtle_index = (i) % 2 + 2
    else:
        turtle_index = (i) % 2 
    print(i,turtle_index)
    
    # 设置乌龟图像的位置（左上角）
    turtle_img_objs[0].set_offset((340, 50))
    turtle_img_objs[1].set_offset((340, 50))
    turtle_img_objs[2].set_offset((340, 50))
    turtle_img_objs[3].set_offset((340, 50))
    
    # 更新乌龟图像
    update_turtle_image(ax, turtle_img_objs, turtle_ims, turtle_index) 


# 创建动画对象
ani = animation.FuncAnimation(fig, update_map, frames=len(data), interval=1000/1, blit=False)

# 调整子图边距以将ax放大到占满屏幕
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
#ax.axis('off')

# 保存动画为视频文件
ani.save('update_map_with_info_animation_t7.mp4', writer='ffmpeg', fps=1, dpi=100)
