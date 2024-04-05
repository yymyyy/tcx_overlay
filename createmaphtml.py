import os
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import csv

def speed_to_pace(speed_mps):
    if speed_mps==0:
        return "0"
    # 计算秒每米
    seconds_per_meter = 1 / speed_mps
    # 将秒每米转换为秒每公里
    seconds_per_km = seconds_per_meter * 1000
    # 转换为分秒每公里的格式
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    # 格式化输出
    pace_str = "{}分{}秒".format(minutes, seconds)
    return pace_str

# # 示例用法
# speed_mps = 3.0  # 米每秒
# pace = speed_to_pace(speed_mps)
# print("Pace:", pace)  # 输出：4'03''
def calculate_time_difference(prev_time, curr_time):
    # 将字符串时间转换为 datetime 对象
    prev_datetime = datetime.strptime(prev_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    curr_datetime = datetime.strptime(curr_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    # 计算时间差
    time_difference = curr_datetime - prev_datetime
    
    # 将时间差转换为秒数
    seconds = time_difference.total_seconds()
    
    # 将秒数转换为 h:mm:ss 格式
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_format = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    
    return time_format

# 解析TCX文件
def parse_tcx_file(tcx_file):
    tree = ET.parse(tcx_file)
    root = tree.getroot()

    # 找到所有的Trackpoint节点
    trackpoints = root.findall('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint')

    # 创建一个列表用于保存提取的数据
    data_list = []

    # 遍历每个Trackpoint
    for trackpoint in trackpoints:
        # 提取时间
        time = trackpoint.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time').text
        
        # 提取纬度和经度
        latitudeleaf = trackpoint.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LatitudeDegrees')
        #print(latitudeleaf)
        latitude = "0.0"    
        longitude = "0.0"    
        if latitudeleaf is not None:
            latitude = latitudeleaf.text
        longitudeleaf = trackpoint.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LongitudeDegrees')
        if longitudeleaf is not None:
            longitude = longitudeleaf.text
        
        # 提取距离
        distance = trackpoint.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters').text
        
        # 提取速度
        speed="0"
        speedleaf = trackpoint.find('.//{http://www.garmin.com/xmlschemas/ActivityExtension/v2}Speed')
        #print(speedleaf)
        if speedleaf is not None:
            speed = speedleaf.text

        # 提取心率
        heart_rate = "0"
        heart_rate_leaf = trackpoint.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm/{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value')
        if heart_rate_leaf is not None:
            heart_rate = heart_rate_leaf.text

        # 提取步频
        cadence = "0"
        cadence_leaf = trackpoint.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Extensions/ns3:TPX/ns3:RunCadence', namespaces={'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'})
        if cadence_leaf is not None:
            cadence = cadence_leaf.text

        # 提取海拔
        altitude = "0.0"
        altitude_leaf = trackpoint.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}AltitudeMeters')
        if altitude_leaf is not None:
            altitude = altitude_leaf.text    
            
        # 将数据保存到字典中
        trackpoint_data = {
            'time': time,
            'latitude': latitude,
            'longitude': longitude,
            'distance': distance,
            'speed': speed,
            'heart_rate': heart_rate,
            'cadence': cadence,
            'altitude': altitude
        }
        
        # 将字典添加到列表中
        data_list.append(trackpoint_data)

    ## 打印前几个Trackpoint的数据
    #for i, trackpoint_data in enumerate(data_list, 1):
    #    print("Trackpoint {}: {}".format(i, trackpoint_data))


    curr_data = data_list[0]
    curr_data['time_delta'] = 0
    curr_data['distance_delta'] = 0
    curr_data['speed_calc'] = 0
    curr_data['index'] = 1
    curr_data['last_lon'] = 0.0
    curr_data['last_lat'] = 0.0
    curr_data['time_pass'] = "0:00:00"
    curr_data['heart_rate'] = 0.0
    curr_data['cadence'] = 0.0
    curr_data['altitude'] = 0.0
    data_list[0] = curr_data

    # 计算time_delta、distance_delta、speed_calc，并附加到原始数据记录中
    for i in range(1, len(data_list)):
        prev_data = data_list[i - 1]
        curr_data = data_list[i]
        
        # 手动转换时间格式并计算time_delta
        prev_time = datetime.strptime(prev_data['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        curr_time = datetime.strptime(curr_data['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        time_delta = (curr_time - prev_time).total_seconds()
        curr_data['time_delta'] = time_delta
        if i>0:
            curr_data['time_pass'] = calculate_time_difference(data_list[0]["time"], curr_data['time'])
            print(curr_data['time_pass'])
        
        # 计算distance_delta
        distance_delta = float(curr_data['distance']) - float(prev_data['distance'])
        curr_data['distance_delta'] = distance_delta
        
        # 计算speed_calc
        if time_delta != 0:
            speed_calc = distance_delta / time_delta
        else:
            speed_calc = 0
        curr_data['speed_calc'] = speed_calc
        curr_data['last_lon'] = prev_data['longitude'] 
        curr_data['last_lat'] = prev_data['latitude']

        # 将计算出的curr_data添加到data_list中，并添加序号
        curr_data['index'] = i + 1
        data_list[i] = curr_data
    #print(data_list)
    # 根据speed_calc值排序，找出速度最大的10个数据，将漂移值设为1，其余为0
    data_list.sort(key=lambda x: x['speed_calc'], reverse=True)
    for i, data in enumerate(data_list):
        data['drift'] = 1 if i < 10 or  data['speed_calc']>6 else 0
    # 根据speed_calc值排序，找出速度最大的10个数据，将漂移值设为1，其余为0
    data_list.sort(key=lambda x: x['index'], reverse=True)
    return data_list


## 提取的经纬度数据
#data_list = [
#    {'time': '2024-01-07T03:09:13.000Z', 'latitude': '24.47104518301785', 'longitude': '118.17600547336042', 'distance': '43610.83984375', 'speed': '3.003999948501587'},
#    {'time': '2024-01-07T03:09:14.000Z', 'latitude': '24.471072843298316', 'longitude': '118.17602089606225', 'distance': '43614.26953125', 'speed': '3.003999948501587'}
#    # 其他经纬度数据...
#]

#def generate_csv(data_list, filename):


def convert_to_csv(data_list, filename):
    print(data_list[0])
    sorted_data = sorted(data_list, key=lambda x: x['index'])  # 按照 index 键排序数据
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = sorted_data[0].keys()  # 使用排序后的第一个字典的键作为字段名
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in sorted_data:
            writer.writerow(item)




def generate_html(data_list, output_file):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Trackpoint Map</title>
        <style>
            html, body {
                width: 100%%;
                height: 100%%;
                margin: 0;
                padding: 0;
            }
            #map {
                width: 100%%;
                height: 100%%;
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            // 初始化地图
            function initMap() {
                var map = new google.maps.Map(document.getElementById('map'), {
                    zoom: 12,
                    center: {lat: %s, lng: %s}, // 设置地图中心点
                    mapTypeId: 'satellite' // 设置地图类型为卫星图像
                });

                // 添加经纬度点到地图
    """ % (data_list[-1]['latitude'],data_list[-1]['longitude'])

    # 添加经纬度点到地图
    for data in data_list:
        #print(data)
        if data["drift"]==0:
            html_content += """
                    var marker = new google.maps.Marker({
                        position: {lat: %s, lng: %s},
                        map: map,
                        title: 'l_lat: %s, l_lng: %s, lat: %s, lng: %s, 打点: %s'+ '\\n'+ '比赛时间: %s'+ '\\n'+ 'raw跑动距离(米): %s'+ '\\n'+ 'raw速度(米/秒): %s 配速 %s'+ '\\n'+ '两点时间(秒): %s'+ '\\n'+ '两点距离(米): %s'+ '\\n'+ '两点间计算速度(米/秒): %s 配速 %s',
                        icon: {
                            url: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png', // 设置图标为绿色
                            scaledSize: new google.maps.Size(20, 20) // 设置图标大小
                        }               
                    });
                    
            """ % (data['latitude'], data['longitude'], data['last_lat'], data['last_lon'], data['latitude'], data['longitude'], data['index'], data['time_pass'], '{:.2f}'.format(float(data['distance'])), '{:.2f}'.format(float(data['speed'])), speed_to_pace(float(data['speed'])), int(data['time_delta']), '{:.2f}'.format(data['distance_delta']), '{:.2f}'.format(data['speed_calc']), speed_to_pace(data['speed_calc']))
        else:
            html_content += """
                    var marker = new google.maps.Marker({
                        position: {lat: %s, lng: %s},
                        map: map,
                        title: 'l_lat: %s, l_lng: %s, lat: %s, lng: %s, 打点: %s'+ '\\n'+ '比赛时间: %s'+ '\\n'+ 'raw跑动距离(米): %s'+ '\\n'+ 'raw速度(米/秒): %s 配速 %s'+ '\\n'+ '两点时间(秒): %s'+ '\\n'+ '两点距离(米): %s'+ '\\n'+ '两点间计算速度(米/秒): %s 配速 %s',
                        icon: {
                            url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png', // 设置图标为红色
                            scaledSize: new google.maps.Size(36, 36) // 设置图标大小
                        }               
                    });
                    
            """ % (data['latitude'], data['longitude'], data['last_lat'], data['last_lon'], data['latitude'], data['longitude'], data['index'], data['time_pass'], '{:.2f}'.format(float(data['distance'])), '{:.2f}'.format(float(data['speed'])), speed_to_pace(float(data['speed'])), int(data['time_delta']), '{:.2f}'.format(data['distance_delta']), '{:.2f}'.format(data['speed_calc']), speed_to_pace(data['speed_calc']))
        #print(data['index'])
        #print(data['last_lat'])
        if int(data['index'])>1 and float(data['last_lat'])>0 and float(data['last_lon'])>0 and float(data['latitude'])>0 and float(data['longitude'])>0:
            #print("not1")
            if data["drift"]==0:
                html_content += """
                        var arrowCoordinates = [
                            {lat: %s, lng: %s},
                            {lat: %s, lng: %s}
                        ];

                        // 在两个点之间绘制箭头
                        var arrow = new google.maps.Polyline({
                            path: arrowCoordinates,
                            icons: [{
                                icon: {
                                    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                                    scale: 3,
                                    fillColor: '#66BBEE',  // 更浅的蓝色
                                    fillOpacity: 1,
                                    strokeWeight: 1
                                },
                                offset: '100%%'
                            }],
                            map: map
                        });           
                        var line = new google.maps.Polyline({
                            path: arrowCoordinates,
                            geodesic: true,
                            strokeColor: '#66BBEE',  // 线的颜色
                            strokeOpacity: 1.0,
                            strokeWeight: 1,
                            map: map
                        });        
                        """ % (data['last_lat'], data['last_lon'], data['latitude'], data['longitude'])
            else:
                html_content += """
                        var arrowCoordinates = [
                            {lat: %s, lng: %s},
                            {lat: %s, lng: %s}
                        ];

                        // 在两个点之间绘制箭头
                        var arrow = new google.maps.Polyline({
                            path: arrowCoordinates,
                            icons: [{
                                icon: {
                                    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                                    scale: 5,
                                    fillColor: 'red',  // 
                                    fillOpacity: 1,
                                    strokeWeight: 1
                                },
                                offset: '100%%'
                            }],
                            map: map
                        });           
                        var line = new google.maps.Polyline({
                            path: arrowCoordinates,
                            geodesic: true,
                            strokeColor: 'red',  // 
                            strokeOpacity: 1.0,
                            strokeWeight: 3,
                            map: map
                        });        
                        """ % (data['last_lat'], data['last_lon'], data['latitude'], data['longitude'])
        #else:
            #print("XXXXXXXXXXXXXXXXXXXXXXX")
    html_content += """
            }
        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDLjfGgYy6tpSBldXS8q_AgD7oEWVWSw3M&callback=initMap" async defer></script>
    </body>
    </html>
    """

    # 将生成的HTML内容保存到文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

# # 调用函数生成HTML文件
# generate_html(data_list)

    # 在这里进行解析和数据提取的操作
    # 你的解析代码


def convert_tcx_to_html(tcx_file):
    data_list = parse_tcx_file(tcx_file)
    output_file = os.path.splitext(tcx_file)[0] + '_AutoGenV01.html'
    csv_file = os.path.splitext(tcx_file)[0] + '_AutoGenV01.csv'
    #generate_html(data_list, output_file)
    convert_to_csv(data_list,csv_file)

def main():
    # 获取当前目录下的所有TCX文件
    tcx_files = [file for file in os.listdir() if file.endswith('.tcx')]
    
    # 遍历每个TCX文件进行转换
    for tcx_file in tcx_files:
        print(f"Converting {tcx_file} to HTML...")
        convert_tcx_to_html(tcx_file)
    
    print("Conversion completed.")

if __name__ == "__main__":
    main()
