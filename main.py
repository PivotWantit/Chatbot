from flask import Flask, request, jsonify, render_template
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

application = Flask(__name__)

blockItem = {"go_to_factory":"60895f85f1a09324e4b3a9de",
             "go_to_series":"60895f94ca885a01fa7e9852",
             "go_to_model":"60895f9a51bb5918f5981b21",
             "go_to_spec":"60895fa0f1fa0324a1b12abc",
             "go_to_storage":"60895fa6ca885a01fa7e9854",
             "go_to_marketprice":"60895faef1a09324e4b3a9e0",
             "go_to_color":"60895ff6561a027398d87111",
             "go_to_check":"60896002e7a4e63fc7a01b98",
             "go_to_list":"60896012561a027398d87113",
             "go_to_item":"6089602c561a027398d87115",
             "go_to_buy":"60896160a0ddb07dd0ca13a0"
            }
@application.route('/purchase/maker',methods=['POST'])
def purchase_maker():
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/maker.csv')
    item = []
    quick = []
    logo = ['https://i.ibb.co/vH7xBJW/logo-apple.png',
            'https://i.ibb.co/T1DWCKR/logo-samsung.png', 
            'https://i.ibb.co/KxcZKvT/logo-lg.png']
    # 이미지를 꼭 URL 형태로 가져와야 하는 것 같아보임.
    for i in df.index:
        item.append({"title":df.iloc[i,1],
                     "description":df.iloc[i,2],
                     "thumbnail":{
                      "imageUrl": df.iloc[i,3],
                     # "fixedRatio": True,
                      #"width":200,
                      #"height":100
                     },
                     "buttons":[
                      {"label":df.iloc[i,4],
                       "action":"block",
                       "messageText":df.iloc[i,4],
                       "blockId":blockItem['go_to_series'],
                       "extra":{
                         'maker':f'{df.iloc[i,0]}'
                       }
                      }
                     ]
                    })

    message = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText": "검색하실 중고폰의 제조사를 선택해주세요."
                    },
                    {
                      "carousel":{
                          "type": "basicCard",
                          "items": item
                      }
                    }                   
                ]
            }
        }
    return message
'''
@application.route('/purchase/market',methods=['POST'])
def set_market():
    url = 'https://wantit.real-seller.com/?main=y&step=condition'
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        dataset = {'ppl_name':[],'ppl_model_code':[],'ppl_storage':[],'ppl_class':[],'ppl_average':[],'ppl_average_move':[]}
        html = BeautifulSoup(response.text,"html.parser")
        data = html.find_all('tbody',attrs={'class':'series_total_big'})
        for i in data:
            items = i.select('tr')
            for j in items[::2]:
                dataset['ppl_name'].append(j.find('th').text.strip())
                tags = j.find_all('td')
                dataset['ppl_model_code'].append(tags[0].text.strip())
                dataset['ppl_storage'].append(tags[1].text.strip().replace("기가",""))
                dataset['ppl_class'].append(tags[2].text.strip())
                dataset['ppl_average'].append(int(tags[3].text.strip().replace("원","").replace(",","")))
                #print(tags[4].get('class'))
                if tags[4].get('class')!= None and tags[4].get('class')[0] == 'down':
                    dataset['ppl_average_move'].append(-int(tags[4].text.strip().replace(",","")))
                elif tags[4].get('class') == None:
                    dataset['ppl_average_move'].append(0)
                else :
                    dataset['ppl_average_move'].append(int(tags[4].text.strip().replace(",","")))
                    
        df = pd.DataFrame(columns=['ppl_name','ppl_model_code','ppl_storage','ppl_class','ppl_average','ppl_average_move'])
        df['ppl_name'] = dataset['ppl_name']
        df['ppl_model_code'] = dataset['ppl_model_code']
        df['ppl_storage'] = dataset['ppl_storage']
        df['ppl_class'] = dataset['ppl_class']
        df['ppl_average'] = dataset['ppl_average']
        df['ppl_average_move'] = dataset['ppl_average_move']
        df.to_csv('/workspace/Data_Analysis/data/marketprice.csv',encoding='utf-8-sig')
'''
@application.route('/purchase/group',methods=['POST'])
def purchase_group():
    response = request.get_json()
    maker = response['action']['clientExtra']['maker']   
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_price_list.csv')
    df2 = df[df['ppl_maker']==maker].copy()
    if maker != 'apple':
        df3 = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_list_group.csv')
        df4 = df3[df3['plg_maker']==maker].copy()
        item = []
        for i in df4.index:
            item.append({"label":df4.loc[i,'plg_group_name'],
                      "action":"block",
                      "messageText":df4.loc[i,'plg_group_name'],
                      "blockID":blockItem['go_to_model'],
                      "extra":{
                       "maker": maker,
                       "group": df4.loc[i,'plg_group']   
                      }
                     })
        message = {
                "version": "2.0",
                "template":{
                    "outputs":[
                        {
                          "simpleText":{
                              "text": f'{maker}전자를 선택하셨군요~\n어떤 시리즈를 원하시나요?'
                          }
                        }                   
                    ],
                    "quickReplies":item
                }
            }
        return message
    else :        
        item = []
        df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
        df2.drop_duplicates(['ppl_model_code'],keep='first',inplace=True)
        df2.reset_index(drop=True,inplace=True)
        for i in df2.index:
            item.append({"title":df2.loc[i,'ppl_name'],
                         "description": df2.loc[i,'ppl_model_code'],
                         "thumbnail":{
                          "imageUrl": f'https://wantit.real-seller.com/images/items/{df2.loc[i,"ppl_maker"]}/{df2.loc[i,"ppl_model_code"]}.jpg',
                          "fixedRatio": True,
                          "width":100,
                          "height":150
                         },
                         "buttons":[
                          {"label":"상세 스펙보기",
                           "action":"block",
                           "messageText":f'{df2.loc[i,"ppl_name"]} 스펙',
                           "blockId":blockItem['go_to_spec'],
                           "extra": {
                               "model_code": df2.loc[i,"ppl_model_code"]
                           }
                          }                    
                         ]

                        })
        message = {
                "version": "2.0",
                "template":{
                    "outputs":[
                        {
                            "simpleText": "세부 모델을 선택하세요."
                        },
                        {
                          "carousel":{
                              "type": "basicCard",
                              "items": item
                          }
                        }                   
                    ],
                }
            }
        return message
    
@application.route('/purchase/model',methods=['POST'])
def purchase_model():
    response = request.get_json()
    maker = response['action']['clientExtra']['maker']   
    group = response['action']['clientExtra']['group']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_price_list.csv')
    df2 = df[(df['ppl_maker']==maker) & (df['ppl_group']==group)].copy()
    df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
    df2.drop_duplicates(['ppl_model_code'],keep='first',inplace=True)
    df2.reset_index(drop=True,inplace=True)
    data = []
    for i in df2.index:
        data.append({"title":df2.loc[i,'ppl_name'],
                     "description":df2.loc[i,'ppl_model_code'],
                     "thumbnail":{
                      "imageUrl": f'https://wantit.real-seller.com/images/items/{df2.loc[i,"ppl_maker"]}/{df2.loc[i,"ppl_model_code"]}.jpg',
                      "fixedRatio": True,
                      "width":100,
                      "height":150
                     },
                     "buttons":[
                      {"label":"상세 스펙보기",
                       "action":"block",
                       "messageText":f'{df2.loc[i,"ppl_name"]} 스펙',
                       "blockId":blockItem['go_to_spec'],
                       "extra": {
                           "model_code": df2.loc[i,'ppl_model_code']
                       }
                      }
                     ]
                    })
    message = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText": "세부 모델을 선택하세요."
                    },
                    {
                      "carousel":{
                          "type": "basicCard",
                          "items": data
                      }
                    }                   
                ],
            }
        }
    return message
@application.route('/purchase/spec',methods=['POST'])
def purchase_spec():
    response = request.get_json()
    model_code = response['action']['clientExtra']['model_code']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_list.csv')
    #df['모델명'] = df['모델명'].str.strip()
    df2 = df[(df['pl_model_code'] == model_code)].copy()
    df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
    df2.reset_index(drop=True,inplace=True)
    message = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                       "basicCard":{
                                "title": f"{df2.loc[0,'pl_name']} ({df2.loc[0,'pl_model_code']})",
                                "description": f"제조사 : {df2.loc[0,'pl_maker']}\n크기 : {df2.loc[0,'pl_display_cm']}cm\n화면 : {df2.loc[0,'pl_display_inch']}인치\n무게 : {df2.loc[0,'pl_weight']}g\n용량 : {df2.loc[0,'pl_storage'].replace('|',',')}GB\n배터리 : {df2.loc[0,'pl_battery']}mAh\n전면카메라 : {df2.loc[0,'pl_front_camera']}\n후면카메라 : {df2.loc[0,'pl_back_camera']}\n색상 : {df2.loc[0,'pl_color_name'].replace('|',',')}",
                                "thumbnail":{
                                    "imageUrl":f'https://wantit.real-seller.com/images/items/{df2.loc[0,"pl_maker"]}/{model_code}.jpg',
                                    "altText":"조회된 이미지가 없습니다.",
                                    "fixedRatio": True,
                                    "width":100,
                                    "height":150
                                },
                                "buttons":[
                                    {
                                      "label":"용량 선택하기",
                                       "action":"block",
                                       "messageText":f'{df2.loc[0,"pl_name"]}',
                                       "blockId":blockItem['go_to_storage'],
                                       "extra": {
                                           "model_code": df2.loc[0,'pl_model_code']
                                       }  
                                    }
                                ]
                           
                        }

                    }
                ]
            }
    }
    return message

@application.route('/purchase/storage',methods=['POST'])
def purchase_storage():
    response = request.get_json()
    model = response['action']['clientExtra']['model_code']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_price_list.csv')    
    df2 = df[(df['ppl_model_code'] == model) & (df['ppl_hidden']==0)].copy()
    df2.reset_index(drop=True,inplace=True)
    storage = df2['ppl_storage'].unique()
    item = []
    for i in storage:
        item.append({"label":f'{i}GB',
                     "action":"block",
                     "messageText":f'{i}GB',
                     "blockId":blockItem['go_to_marketprice'],
                     "extra":{
                             "model_code": model,
                             "storage": i
                         }
                     })
    message = {
        "version": "2.0",
        "template":{
            "outputs":[
                {"simpleText" : f"짠~ {df2['ppl_name'][0]}까지 선택하셨습니다.\n용량은 어느 정도로 생각하시나요?"}],
            "quickReplies": item
        }
    }

    return message 

@application.route('/purchase/marketprice',methods=['POST'])
def purchase_market():
    response = request.get_json()
    model = response['action']['clientExtra']['model_code']
    storage = response['action']['clientExtra']['storage']
    #print(model,storage,type(model),type(storage))
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_price_list.csv')    
    df2 = df[(df['ppl_model_code'] == model) & (df['ppl_storage'] == storage) & (df['ppl_hidden']==0)].copy()
    df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
    df2.reset_index(drop=True,inplace=True)
    #df2.to_csv('/workspace/Data_Analysis/data/test4.csv',encoding='utf-8-sig')
    item = []
    quick = []
    for i in df2.index:
        item.append({"title": f'{df2.loc[i,"ppl_name"]} {df2.loc[i,"ppl_storage"]}GB {df2.loc[i,"ppl_class"]}급',
                     "description": f'{df2.loc[i,"ppl_average"]}원 (변동금액 : {df2.loc[i,"ppl_average"]-df2.loc[i,"ppl_average_old"]}원)'
                    })
        quick.append({"label":f'{df2.loc[i,"ppl_class"]}급 조회하기',
                     "action":"block",
                     "messageText":f'{df2.loc[i,"ppl_name"]} {df2.loc[i,"ppl_storage"]}GB {df2.loc[i,"ppl_class"]}급 조회',
                     "blockId":blockItem['go_to_color'],
                     "extra":{
                             "model_code": model,
                             "storage": df2.loc[i,'ppl_storage'],
                             "class": df2.loc[i,'ppl_class']
                         }
                     })
    message = {
        "version": "2.0",
        "template":{
            "outputs":[
                {
                  "simpleText": "여기서 잠깐! 등급에 대해 알려드려요.\n[S급]: 거의 새것처럼 깨끗하면 좋겠어요.\n[A급]: 주변에 찍힘이 조금 있는 것 까지는 괜찮아요.\n[B급]: 케이스를 사용할 거라서 상태는 중요하지 않아요."
                },
                {"listCard":{
                        "header":{
                            "title":f'현재 중고 시세'
                        },
                        "items":item
                   }
                },        
                {
                  "simpleText": f'{df2.loc[0,"ppl_name"]}의 등급을 골라주세요~'
                }
            ],
            "quickReplies": quick
        }
    }

    return message 

@application.route('/purchase/color',methods=['POST'])
def purchase_color():
    response = request.get_json()
    model = response['action']['clientExtra']['model_code']
    storage = response['action']['clientExtra']['storage']
    level = response['action']['clientExtra']['class']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_write_realseller2.csv')  
    #df['wi_code'] = df['wi_code'].str.strip()
    df2 = df[(df['wi_code'] == model) & (df['wi_storage'] == storage) & (df['wi_class'] == level) & (df['wi_color']!="N")].copy()
    #df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
    df2.reset_index(drop=True,inplace=True)
    color = df2['wi_color'].value_counts()
    item = []  
    if len(color)==0:
        item.append({"label":f'다시 선택하기',
                     "action":"block",
                     "messageText":f'다시 선택하기',
                     "blockId":blockItem['go_to_marketprice'],
                     "extra":{
                         "model_code": model,
                         "storage": storage
                     }
                 })
        message = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText": {"text": "조회된 상품이 없습니다."}
                    }
                ],
                "quickReplies": item
            }
        }
    else :
        for i in color.index:
             item.append({"label":f'{i} ({color[i]}개)',
                           "action":"block",
                           "messageText":f'{i}',
                           "blockId":blockItem['go_to_check'],
                           "extra":{
                                 "model_code": model,
                                 "storage": storage,
                                 "class": level,
                                 "color": i
                             }
                         })
        message = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText": {"text": "색상은 어떤 컬러가 좋을까요?\n(괄호안의 숫자는 상품개수)"}
                    }
                ],
                "quickReplies": item
            }
        }

    return message 
@application.route('/purchase/check',methods=['POST'])
def purchase_choice():
    response = request.get_json()
    model = response['action']['clientExtra']['model_code']
    storage = response['action']['clientExtra']['storage']
    level = response['action']['clientExtra']['class']
    color = response['action']['clientExtra']['color']
    
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_price_list.csv')  
    df2 = df[df['ppl_model_code'] == model].copy()
    df2.reset_index(drop=True,inplace=True)
    maker = df2['ppl_maker'][0]
    df2['ppl_group'].replace('apple','아이폰',inplace=True)
    group = df2['ppl_group'][0]
    name = df2['ppl_name'][0]
    message = {
        "version": "2.0",
        "template":{
            "outputs":[
                {
                   "basicCard":{
                       "title": "선택하신 상품의 스펙입니다.",
                       "description": f'제조사: {maker}\n시리즈: {group}\n모델명: {name}\n용량: {storage}GB\n색상: {color}\n등급: {level}급',
                       "thumbnail":{
                           "imageUrl": f'https://wantit.real-seller.com/images/items/{maker}/{model}.jpg',
                           "fixedRatio": True,
                           "width":100,
                           "height":150
                       },
                       "buttons":[
                           {
                               "label": "다시 선택하기",
                               "action": "block",
                               "messageText": "처음으로",
                               "blockId": blockItem['go_to_factory']
                           },
                           {
                               "label": "상품 조회하기",
                               "action": "block",
                               "messageText": "상품 조회",
                               "blockId": blockItem['go_to_list'],
                               "extra":{
                                   "model_code": model,
                                   "storage": storage,
                                   "class": level,
                                   "color": color
                               }
                           }            
                       ]
                   }
                }
            ]
        }
    }
    return message 

@application.route('/purchase/list',methods=['POST'])
def purchase_list():
    response = request.get_json()
    model = response['action']['clientExtra']['model_code']
    storage = response['action']['clientExtra']['storage']
    level = response['action']['clientExtra']['class']
    color = response['action']['clientExtra']['color']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_write_realseller2.csv')  
    shop_info = {'Phone85':"폰85",'bunjang':"번개장터",'coupang':"쿠팡",'naver':"중고나라"}
    df['wi_code'] = df['wi_code'].str.strip()
    df2 = df[(df['wi_code'] == model) & (df['wi_storage'] == storage) & (df['wi_class'] == level) & (df['wi_color'] == color)].copy()
   # print(df2)
    #df2.drop(['Unnamed: 0'], axis = 1, inplace = True)
    df2.reset_index(drop=True,inplace=True)
    item = []
    for i in df2.index:
         item.append({"description": df2.loc[i,'wr_subject'],
                      "price": int(df2.loc[i,'wr_2']),
                      "currency": "won",
                      "thumbnails":[{
                          "imageUrl": df2.loc[i,'wr_11'].replace("{res}","%7Bres%7D")
                      }],
                      "profile":{
                          "nickname": f"판매사이트: {shop_info[df2.loc[i,'wr_6']]}"
                      },
                      "buttons":[
                          {
                               "label":"자세히 보기",
                               "action":"block",
                               "messageText":"세부 상품 조회",
                               "blockId":blockItem['go_to_item'],
                               "extra": {
                                   "id": str(df2.loc[i,'wr_id'])
                               }  
                          }
                      ]
                     })
    message = {
        "version": "2.0",
        "template":{
            "outputs":[
                {
                    "carousel":{
                        "type": "commerceCard",
                        "items": item
                    }
                }
            ],
            #"quickReplies": item
        }
    }
    return message 


@application.route('/purchase/item',methods=['POST'])
def purchase_item():
    response = request.get_json()
    id = int(response['action']['clientExtra']['id'])
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_write_realseller2.csv')  
    #df['wi_code'] = df['wi_code'].str.strip()
    df2 = df[df['wr_id'] == id].copy()
    df2.reset_index(drop=True,inplace=True)
    
    item = []
    seller = []
    img = df2.loc[0,'img_all'].split('|')
    for i in img:
        item.append({"thumbnail":{
                                 "imageUrl": i.replace("{res}","%7Bres%7D"),
                                 "link": {"web" : i},
                                 "fixedRatio": True,
                                 "width":100,
                                 "height":150,
                                 }
                    })
        
    if df2.loc[0,'wi_choice'] == 2:
        choice = "https://www.analogouscolors.com/image/800x600/90ee90.jpg"
    else :
        choice = ''
    seller.append({"description": df2.loc[0,'wr_subject'],
                  "price": int(df2.loc[0,'wr_2']),
                  "currency": "won",
                  "profile":{
                      "nickname": f"판매자: {df2.loc[0,'wr_10'].split('|')[0]}",
                      "imageUrl": choice
                  },

                  "buttons":[{
                      "label": "상품 원문보기",
                      "action": "webLink",
                      "webLinkUrl": df2.loc[0,'wr_8']
                  }]
                  })
    
    quick = []
    quick.append({"label": "처음으로",
                  "action": "block",
                  "blockId": blockItem['go_to_factory']
                 })
    '''
    quick.append({"label": "구매하기",
              "action": "block",
              "blockId": blockItem['go_to_buy'],
              "clientExtra":{"product_id":id}
             })'''
    message = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                   "carousel":{
                       "type": "commerceCard",
                       "items" : seller
                   }
                },
                {
                    "simpleText": {
                        "text": df2.loc[0,'wr_9']
                    }
                },
                {
                   "carousel":{
                       "type": "basicCard",
                       "items" : item
                   }
                }
            ],
            "quickReplies": quick
        }
    }
    return message 
@application.route('/purchase/buy',methods=['POST'])
def purchase_buyer():
    response = request.get_json()
    message = {"version":"2.0",
              "template":{
                  "outputs":[
                      {
                      "simpleText": {
                          "text": "현재 구매 기능은 준비중입니다."
                          }
                      }
                  ]
              }}
    return message
@application.route('/event/list',methods=['POST'])
def event_load():
    dataset = {'name':[], 'tag':[],'img':[],'link':[]}
    url = 'https://wantit.real-seller.com/?step=planning_list'
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        html = BeautifulSoup(response.text,"html.parser")
        data = html.find_all('div',attrs={'class':'planning_list'})
        for i in data:   
            dataset['name'].append(i.find_all('b')[0].text.strip())
            dataset['tag'].append(i.find_all('b')[1].text.strip())
            dataset['img'].append(i.find('img')['src'])
            dataset['link'].append("https://wantit.real-seller.com/"+i.find('a')['href'][1:])
    df=pd.DataFrame(columns=['name','tag','img','link'])
    df['name'] = dataset['name']
    df['tag'] = dataset['tag']
    df['img'] = dataset['img']
    df['link'] = dataset['link']
        
    df.to_csv('/workspace/RealSeller-ChatBot/data/event.csv',encoding='utf-8-sig')
    result = []
    for i in df.index:
        result.append({"title":df.iloc[i,0],
                       "description":df.iloc[i,1],
                       "thumbnail":{
                           "imageUrl":df.iloc[i,2]
                       },
                      "buttons":[
                          {
                              "action": "webLink",
                              "label": "웹에서 자세히 보기",
                              "webLinkUrl": df.iloc[i,3]
                          }
                      ]})
    message = {
        "version": "2.0",
        "template": {
            "outputs":[
                {
                    "carousel": {
                    "type": "basicCard",
                    "items": result
                    }
                }
            ]
        }
    }
    return message
@application.route('/notice/page2', methods=['POST'])
def get_notice2():
    dataset = {'name': [], 'link': [], 'author': [], 'date': []}
    df = pd.DataFrame(columns=['name', 'link', 'date'])

    url = 'https://wantit.real-seller.com/main_alarm_ajax.php?'

    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser")

    data = html.find_all('li', attrs={'class': 'alarm-wrapper__list'})
    data_link = []

    for i in data:
        data_link.append(i.find('a', attrs={'class': 'alarm-wrapper__list__a'})['onclick'])
        dataset['name'].append(i.select('a>span:first-child')[0].text.strip())
        dataset['date'].append(i.select('a>span:last-child')[0].text.strip())

    link_rev = []

    for i in data_link:
        link_rev.append(i.replace("modalOutLink('공지', '", ""))

    link_rev2 = []
    for index, i in enumerate(link_rev):
        dataset['link'].append(i.replace("')", ""))

    dataset['name'].pop(-1)
    dataset['link'].pop(-1)
    dataset['date'].pop(-1)

    dataset['name'].append('[도움말] 중고 사기거래 예방법(사기 수법 안내)')
    dataset['link'].append('https://blog.naver.com/real-seller/222030744609')
    dataset['date'].append('2021-03-23')

    df['name'] = dataset['name']
    df['link'] = dataset['link']
    df['date'] = dataset['date']
    df.to_csv('./News.csv', encoding='utf-8-sig')
    result = []
    for name, link, date in zip(df['name'], df['link'], df['date']):
        result.append({"title": name,
                       "description": date,
                       "link": {
                           "web": link
                       }})
    message = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "listCard": {
                        "header": {
                            "title": "공지사항을 알려드립니다."
                        },
                        "items": result[4:],
                        "buttons": [
                            {
                                "label": "이전으로 돌아가기",
                                "action": "message",
                                "messageText": "공지사항"
                            }
                        ]
                    }
                }
            ]
        }
    }
    print(message)
    return message


@application.route('/notice/page1', methods=['POST'])
def get_notice1():
    dataset = {'name': [], 'link': [], 'author': [], 'date': []}
    df = pd.DataFrame(columns=['name', 'link', 'date'])

    url = 'https://wantit.real-seller.com/main_alarm_ajax.php?'

    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser")

    data = html.find_all('li', attrs={'class': 'alarm-wrapper__list'})
    data_link = []

    for i in data:
        data_link.append(i.find('a', attrs={'class': 'alarm-wrapper__list__a'})['onclick'])
        dataset['name'].append(i.select('a>span:first-child')[0].text.strip())
        dataset['date'].append(i.select('a>span:last-child')[0].text.strip())

    link_rev = []

    for i in data_link:
        link_rev.append(i.replace("modalOutLink('공지', '", ""))

    link_rev2 = []
    for index, i in enumerate(link_rev):
        dataset['link'].append(i.replace("')", ""))

    dataset['name'].pop(-1)
    dataset['link'].pop(-1)
    dataset['date'].pop(-1)

    dataset['name'].append('[도움말] 중고 사기거래 예방법(사기 수법 안내)')
    dataset['link'].append('https://blog.naver.com/real-seller/222030744609')
    dataset['date'].append('2021-03-23')

    df['name'] = dataset['name']
    df['link'] = dataset['link']
    df['date'] = dataset['date']
    df.to_csv('./News.csv', encoding='utf-8-sig')
    result = []
    for name, link, date in zip(df['name'], df['link'], df['date']):
        result.append({"title": name,
                       "description": date,
                       "link": {
                           "web": link
                       }})
    message = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "listCard": {
                        "header": {
                            "title": "공지사항을 알려드립니다."
                        },
                        "items": result[:4],
                        "buttons": [
                            {
                                "label": "공지사항 더보기",
                                "action": "message",
                                "messageText": "공지사항 더보기"
                            }
                        ]
                    }
                }
            ]
        }
    }
    print(message)
    return message


@application.route('/oldnotice/page2', methods=['POST'])
def get_old_notice2():
    dataset = {'name': [], 'link': [], 'author': [], 'date': []}
    url = 'https://real-seller.com/bbs/board.php?bo_table=notice'
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        html = BeautifulSoup(response.text, "html.parser")
        data = html.select('tbody tr')
        for i in data[1:]:
            try:
                test = i.select('a')[0].select('span')[0].text.strip()
                dataset['name'].append(i.select('a')[0].text.strip()[:-10].strip())
            except:
                dataset['name'].append(i.select('a')[0].text.strip())

            dataset['link'].append(i.select('a')[0]['href'])
            dataset['author'].append(i.select('.td_name')[0].text.strip())
            dataset['date'].append(i.select('.td_date')[0].text.strip())
        df = pd.DataFrame(columns=['name', 'link', 'author', 'date'])
        df['name'] = dataset['name']
        df['link'] = dataset['link']
        df['author'] = dataset['author']
        df['date'] = dataset['date']

        df.to_csv('./oldNews.csv', encoding='utf-8-sig')
        result = []
        for name, link, author, date in zip(df['name'], df['link'], df['author'], df['date']):
            result.append({"title": name,
                           "description": author + " " + date,
                           "link": {
                               "web": link
                           }})
        message = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "listCard": {
                            "header": {
                                "title": "공지사항을 알려드립니다."
                            },
                            "items": result[5:]

                        }
                    }
                ]
            }
        }
        print(message)
        return message
    else:
        print("Connection Error")
        result = "조회된 데이터가 없습니다"
        message = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": result
                        }
                    }
                ]
            }
        }
        return message


@application.route('/oldnotice/page1', methods=['POST'])
def get_old_notice():
    dataset = {'name': [], 'link': [], 'author': [], 'date': []}
    url = 'https://real-seller.com/bbs/board.php?bo_table=notice'
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        html = BeautifulSoup(response.text, "html.parser")
        data = html.select('tbody tr')
        for i in data[1:]:
            try:
                test = i.select('a')[0].select('span')[0].text.strip()
                dataset['name'].append(i.select('a')[0].text.strip()[:-10].strip())
            except:
                dataset['name'].append(i.select('a')[0].text.strip())

            dataset['link'].append(i.select('a')[0]['href'])
            dataset['author'].append(i.select('.td_name')[0].text.strip())
            dataset['date'].append(i.select('.td_date')[0].text.strip())
        df = pd.DataFrame(columns=['name', 'link', 'author', 'date'])
        df['name'] = dataset['name']
        df['link'] = dataset['link']
        df['author'] = dataset['author']
        df['date'] = dataset['date']

        df.to_csv('./oldNews.csv', encoding='utf-8-sig')
        result = []
        for name, link, author, date in zip(df['name'], df['link'], df['author'], df['date']):
            result.append({"title": name,
                           "description": author + " " + date,
                           "link": {
                               "web": link
                           }})
        message = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "listCard": {
                            "header": {
                                "title": "공지사항을 알려드립니다."
                            },
                            "items": result[:5],
                            "buttons": [
                                {
                                    "label": "공지사항 더보기",
                                    "action": "message",
                                    "messageText": "공지사항 더보기"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        print(message)
        return message
    else:
        print("Connection Error")
        result = "조회된 데이터가 없습니다"
        message = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": result
                        }
                    }
                ]
            }
        }
        return message
'''
@application.route('/event/setting',methods=['POST'])
def set_event():
    dataset = {'link':[],'explain_img':[]}
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/event.csv')
    for i in df.index:
        url = df.iloc[i,4]
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            html = BeautifulSoup(response.text,"html.parser")
            data =html.find_all('img',attrs={'class':'main_img'})
            dataset['link'].append(url)
            dataset['explain_img'].append(data[0]['src'])
    df['explain_img'] = dataset['explain_img']
    df.to_csv('/workspace/RealSeller-ChatBot/data/event.csv',encoding='utf-8-sig')
    message = {
        "version": "2.0",
        "template":{
            "outputs":[
                {
                  "simpleText": {
                    "text": "ok"
                    }  
                }
            ]
        }
    }
    return message

@application.route('/event/product',methods=['POST'])
def get_event():
    response = request.get_json()
    number = response['action']['clientExtra']['number']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/event.csv')
    message = {
            "version": "2.0",
            "template":{
                "outputs":[
                      {
                          "simpleImage": {
                                            "imageUrl": df.iloc[number,6],
                                            "altText": "기획전 세부사항입니다"
                                        }
                      }
                ]
            }
        }
    return message
'''

'''//////////////// 전문가 문의 ////////////////////'''
'''
go_to_manufacture = '60881ec451bb5918f59811fc'
go_to_model = '60881ee5561a027398d86749'
go_to_series = '60881ed9f1a09324e4b3a0ae'
go_to_capacity = '60881efa08b1647562b8997d'
go_to_color = '60881f2ff1a09324e4b3a0b0'
go_to_grade = '60881f50ca885a01fa7e8f35'
go_to_additional = '60881f6808b1647562b8997f'
go_to_send =  '60881f70a0ddb07dd0ca0a46'
'''
expert_blockItem = {"go_to_manufacture":"60881ec451bb5918f59811fc",
             "go_to_series":"60881ed9f1a09324e4b3a0ae",
             "go_to_model":"60881ee5561a027398d86749",
             "go_to_capacity":"60881efa08b1647562b8997d",
             "go_to_color":"60881f2ff1a09324e4b3a0b0",
             "go_to_grade":"60881f50ca885a01fa7e8f35",
             "go_to_additional":"60881f6808b1647562b8997f",
             "go_to_nonmember":"60881f70a0ddb07dd0ca0a46"
            }

@application.route('/expert/manufacture',methods=['POST'])
def expert_factory():
    response = request.get_json()
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_list.csv')
    df2 = df['pl_maker'].unique()
    quick = []
    for i in df2:
        quick.append({"label":i,
                      "action":"block",
                      "messageText":i,
                      "blockId":expert_blockItem['go_to_model'],
                      "extra":{
                       "manufacture":i    
                      }
                     })
    message = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                      "simpleText":{
                          "text": "[전문가 문의] 제조사 선택"
                      }
                    },
                    {
                      "simpleText":{
                          "text": "문의하려는 기기의 제조사를 선택해주세요."
                      }
                    }
                ],
                "quickReplies":quick
            }
        }
    return message


@application.route('/expert/model',methods=['POST'])
def expert_model():
    response = request.get_json()
    manufacture = response['action']['clientExtra']['manufacture']   
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_list.csv')
    df2 = df[df['pl_maker']==manufacture]
    if manufacture != 'apple':
        series = df2['pl_group'].unique()
        quick = []
        for i in series:
            if i != "samsung":
                quick.append({"label":i,
                          "action":"block",
                          "messageText":i,
                          "blockId":expert_blockItem['go_to_series'],
                          "extra":{
                           "manufacture": manufacture,
                           "series":i    
                          }
                         })
            else:
                quick.append({"label":"기타",
                          "action":"block",
                          "messageText":"기타",
                          "blockId":expert_blockItem['go_to_series'],
                          "extra":{
                           "manufacture": manufacture,
                           "series":i   
                          }
                         })
            quick.sort(key=lambda x: x['label'], reverse=False)
        quick.insert(0, {"label":"다시 선택하기",
                      "action":"block",
                      "messageText":"다시 선택하기",
                      "blockId":expert_blockItem['go_to_manufacture']
                     })
        message = {
                "version": "2.0",
                "template":{
                    "outputs":[
                        {
                             "simpleText":{
                                 "text": "[전문가 문의] 시리즈 선택"
                             }
                        },
                        {
                          "simpleText":{
                              "text":"문의하려는 기기의 시리즈를 선택하세요."
                          }
                        }                   
                    ],
                    "quickReplies":quick
                }
            }
        return message
    else:
        quick = []
        quick.append({"label":"다시 선택하기",
                      "action":"block",
                      "messageText":"다시 선택하기",
                      "blockId":expert_blockItem['go_to_manufacture']
                     })
        for i in df2.index:
            quick.append({"label":df.iloc[i,5],
                      "action":"block",
                      "messageText":df.iloc[i,5],
                      "blockId":expert_blockItem['go_to_capacity'],
                      "extra":{
                       "manufacture": manufacture,
                       "series": 'apple',
                       "model":df.iloc[i,4]
                      }
                     })
        message = {
                "version": "2.0",
                "template":{
                    "outputs":[
                        {
                             "simpleText":{
                                 "text": "[전문가 문의] 모델 선택"
                             }
                        },
                        {
                             "simpleText":{
                                 "text":"문의하려는 기기의 모델을 선택하세요."
                             }
                        }                   
                    ],
                    "quickReplies":quick
                }
            }
        return message


@application.route('/expert/series',methods=['POST'])
def expert_series():
    response = request.get_json()
    manufacture = response['action']['clientExtra']['manufacture']   
    series = response['action']['clientExtra']['series']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_list.csv')
    df2 = df[(df['pl_maker']==manufacture) & (df['pl_group']==series)]
    df2.reset_index(drop=True,inplace=True)
    quick = []
    quick.append({"label":"다시 선택하기",
                  "action":"block",
                  "messageText":"다시 선택하기",
                  "blockId":expert_blockItem['go_to_manufacture']
                 })
    for i in df2.index:
        quick.append({"label":df2.iloc[i,5],
                      "action":"block",
                      "messageText":df2.iloc[i,5],
                      "blockId":expert_blockItem['go_to_capacity'],
                      "extra":{
                       "manufacture": manufacture,
                       "series":series,
                       "model":df2.iloc[i,4]   
                      }
                     })
    message = {
                "version": "2.0",
                "template":{
                    "outputs":[
                        {
                             "simpleText":{
                                 "text": "[전문가 문의] 모델 선택"
                             }
                        },
                        {
                             "simpleText":{
                                 "text":"문의하려는 기기의 모델을 선택하세요."
                             }
                        }
                    ],
                    "quickReplies":quick
                }
            }
    return message

@application.route('/expert/capacity',methods=['POST'])
def expert_capacity():
    response = request.get_json()
    manufacture = response['action']['clientExtra']['manufacture'] 
    series = response['action']['clientExtra']['series']
    model = response['action']['clientExtra']['model']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_list.csv')
    df2 = df[(df['pl_maker']==manufacture) & (df['pl_group']==series) & (df['pl_model_code']==model)]
    df2.reset_index(drop=True,inplace=True)
    quick = []
    quick.append({"label":"다시 선택하기",
                  "action":"block",
                  "messageText":"다시 선택하기",
                  "blockId":expert_blockItem['go_to_manufacture']
                 })
    for i in df2.index: 
        cap = (df2.iloc[i,7]).split('|')
        for j in range(len(cap)):
            quick.append({"label":cap[j] + "GB",
                          "action":"block",
                          "messageText":cap[j] + "GB",
                          "blockId":expert_blockItem['go_to_color'],
                          "extra":{
                           "manufacture": manufacture,
                           "series":series,
                           "model":model,
                           "capacity":cap[j] + "GB"
                          }
                     })
    message = {
                "version": "2.0",
                "template":{
                    "outputs":[
                        {
                             "simpleText":{
                                 "text": "[전문가 문의] 용량 선택"
                             }
                        },
                        {
                             "simpleText":{
                                 "text":"문의하려는 기기의 용량(단위:GB)을 선택하세요."
                             }
                        }
                    ],
                    "quickReplies":quick
                }
            }
    return message

@application.route('/expert/color',methods=['POST'])
def expert_color():
    response = request.get_json()
    manufacture = response['action']['clientExtra']['manufacture'] 
    series = response['action']['clientExtra']['series']
    model = response['action']['clientExtra']['model']
    capacity = response['action']['clientExtra']['capacity']
    df = pd.read_csv('/workspace/RealSeller-ChatBot/data/g5_phone_list.csv')
    df2 = df[(df['pl_maker']==manufacture) & (df['pl_group']==series) & (df['pl_model_code']==model)]
    df2.reset_index(drop=True,inplace=True)
    quick = []
    quick.append({"label":"다시 선택하기",
                  "action":"block",
                  "messageText":"다시 선택하기",
                  "blockId":expert_blockItem['go_to_manufacture']
                 })
    for i in df2.index: 
        colors = (df2.iloc[i,8]).split('|')
        for j in range(len(colors)):
            quick.append({"label":colors[j],
                          "action":"block",
                          "messageText":colors[j],
                          "blockId":expert_blockItem['go_to_grade'],
                          "extra":{
                           "manufacture": manufacture,
                           "series":series,
                           "model":model,
                           "capacity":capacity,
                           "color":colors[j],
                           "color_num":colors.index(colors[j])
                          }
                     })
    message = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                      "simpleText":{
                          "text": "[전문가 문의] 색상 선택"
                      }
                    },
                    {
                      "simpleText":{
                          "text": "문의하려는 기기의 색상을 선택해주세요."
                      }
                    }
                ],
                "quickReplies":quick
            }
        }
    return message

@application.route('/expert/grade',methods=['POST'])
def expert_grade():
    response = request.get_json()
    manufacture = response['action']['clientExtra']['manufacture'] 
    series = response['action']['clientExtra']['series']
    model = response['action']['clientExtra']['model']
    capacity = response['action']['clientExtra']['capacity']
    color = response['action']['clientExtra']['color']
    color_num = response['action']['clientExtra']['color_num']
    grades=['S','A','B','상관없음']
    grades_send=['S','A','B','N']
    quick = []
    quick.append({"label":"다시 선택하기",
                  "action":"block",
                  "messageText":"다시 선택하기",
                  "blockId":expert_blockItem['go_to_manufacture']
                 })
    for i in range(len(grades)):
        quick.append({"label":grades[i],
                      "action":"block",
                      "messageText":grades[i],
                      "blockId":expert_blockItem['go_to_additional'],
                      "extra":{
                       "manufacture": manufacture,
                       "series":series,
                       "model":model,
                       "capacity":capacity,
                       "color":color,
                       "color_num":color_num,
                       "grade":grades_send[i]
                      }
                    })
    message = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                      "simpleText":{
                          "text": "[전문가 문의] 등급 선택"
                      }
                    },
                    {
                      "simpleText":{
                          "text": "문의하려는 기기의 등급을 선택해주세요."
                      }
                    }
                ],
                "quickReplies":quick
            }
        }
    return message

@application.route('/expert/additional',methods=['POST'])
def expert_additional():
    response = request.get_json()
    manufacture = response['action']['clientExtra']['manufacture']
    series = response['action']['clientExtra']['series']
    model = response['action']['clientExtra']['model']
    capacity = response['action']['clientExtra']['capacity']
    color = response['action']['clientExtra']['color']
    color_num = response['action']['clientExtra']['color_num']
    grade = response['action']['clientExtra']['grade']
    additional = response['action']['params']['additional']
    
    #print(manufacture,type(manufacture),series,type(series),model,type(model),capacity,type(capacity),color,type(color),grade,type(grade),additional,type(additional))
    response['action']['clientExtra']['additional'] = additional
    response = str(response['action']['clientExtra']['additional'])

    data = []
    data.append({
                "extra":{
                    "manufacture": manufacture,
                    "series":series,
                    "model":model,
                    "capacity":capacity,
                    "color":color,
                    "color_num":color_num,
                    "grade":grade,
                    "additional":response
                    }
                })
    quick = []
    quick.append({"label":"문의하기",
                  "action":"block",
                  "messageText":"문의하기",
                  "blockId":'608fe45ef1fa0324a1b14bc0',#expert_blockItem['go_to_send'] '''인증블록으로 넘기면 회원인지 확인''',
                  "extra":{"data":data}
                 })
    quick.append({"label":"다시 선택하기",
                  "action":"block",
                  "messageText":"다시 선택하기",
                  "blockId":expert_blockItem['go_to_manufacture']
                 })
    

    if series == "apple" :
        message = {
                "version": "2.0",
                "template":{
                    "outputs":[
                        {
                          "simpleText":{
                              "text": "문의하신 상품의 스펙입니다."
                          }
                        },
                        {
                          "simpleText":{
                              "text": "제조사 : " + manufacture +"\n" +
                                      "모델명 : " + model +"\n" +
                                      "용량 : " + capacity +"\n" +
                                      "색상 : " + color +"\n" +
                                      "등급 : " + grade +"\n" +
                                      "추가 문의 사항 : " + response
                          }
                        },
                        {
                            "simpleText":{
                                "text": "문의하려는 상품이 맞다면 '문의하기' 를 눌러주시고,\n다시 상품을 선택하려면 '다시 선택하기'를 눌러주세요."
                            }
                        }
                    ],"quickReplies":quick
                }
            }
    else :
        if series == "samsung" or "lg": 
            message = {
                    "version": "2.0",
                    "template":{
                        "outputs":[
                            {
                              "simpleText":{
                                  "text": "문의하신 상품의 스펙입니다."
                              }
                            },
                            {
                              "simpleText":{
                                  "text": "제조사 : " + manufacture +"\n" +
                                          "시리즈 : " + "기타" +"\n" +
                                          "모델명 : " + model +"\n" +
                                          "용량 : " + capacity +"\n" +
                                          "색상 : " + color +"\n" +
                                          "등급 : " + grade +"\n" +
                                          "추가 문의 사항 : " + response
                              }
                            },
                            {
                                "simpleText":{
                                    "text": "문의하려는 상품이 맞다면 '문의하기' 를 눌러주시고,\n다시 상품을 선택하려면 '다시 선택하기'를 눌러주세요."
                                }
                            }
                        ],"quickReplies":quick
                    }
                }
        else : 
            message = {
                    "version": "2.0",
                    "template":{
                        "outputs":[
                            {
                              "simpleText":{
                                  "text": "문의하신 상품의 스펙입니다."
                              }
                            },
                            {
                              "simpleText":{
                                  "text": "제조사 : " + manufacture +"\n" +
                                          "시리즈 : " + series +"\n" +
                                          "모델명 : " + model +"\n" +
                                          "용량 : " + capacity +"\n" +
                                          "색상 : " + color +"\n" +
                                          "등급 : " + grade +"\n" +
                                          "추가 문의 사항 : " + response
                              }
                            },
                            {
                                "simpleText":{
                                    "text": "문의하려는 상품이 맞다면 '문의하기' 를 눌러주시고,\n다시 상품을 선택하려면 '다시 선택하기'를 눌러주세요."
                                }
                            }
                        ],"quickReplies":quick
                    }
                }
    return message
    
    
@application.route('/expert/nonuser',methods=['POST'])
def expert_nonuser():
    response = request.get_json()
    print(response)
    user_data = response['action']['params']
    user_mail = response['action']['clientExtra']['mb_email']
    print(user_data,type(user_data))
    input_data = response['action']['clientExtra']['data']
    print(input_data,type(input_data))
    
    data = response['action']['clientExtra']
    send_url = f'http://wantit.real-seller.com/api/wantit_api.php?api_type=1&request_url=https://realseller-chatbot.run.goorm.io/profile/data2&mb_email='
    send_data = f"{user_mail}&maker={input_data['manufacture']}&series={input_data['series']}&model={input_data['model']}&storage={input_data['capacity'].replace('GB','')}&color={input_data['color_num']}&condition={input_data['grade']}&memo={input_data['additional']}&mb_name={user_data['mb_name']}&mb_pw={user_data['mb_pw']}&mb_hp_1=0{data['mb_ph_1']}&mb_ph_2={data['mb_ph_2']}&mb_ph_3={data['mb_ph_3']}"
    print(send_url+send_data)
        
    message = {
           "version": "2.0",
           "template":{
               "outputs":[
                   {
                     "simpleText":{
                         #"text": "전문가 문의가 완료되었습니다.\n문의 결과는 2~3일 내에 메일로 전송됩니다."
                         "text": "현재 전문가 문의 등록은 준비중입니다."
                     }
                   }
                ]
            }
        }
    return message

@application.route('/expert/send',methods=['POST'])
def expert_send():
    response = request.get_json()
    message = {
           "version": "2.0",
           "template":{
               "outputs":[
                   {
                     "simpleText":{
                         #"text": "전문가 문의가 완료되었습니다.\n문의 결과는 2~3일 내에 메일로 전송됩니다."
                         "text": "현재 전문가 문의 등록은 준비중입니다."
                     }
                   }
                ]
            }
        }
    return message

@application.route('/profile/data',methods=['POST'])
def find_user():
    response = request.get_json()
    origin = response['value']['origin']
    key = '8e723be918ebe889c1e8b169396cfa46'
    
    result = {
        "status": "SUCCESS",
        "value": f'{origin}?rest_api_key={key}',
        "message": "OK"
    }
    '''
    response2 = requests.get(f'{origin}?rest_api_key={key}')
    user_data = json.loads(response2.text)
    #print(user_data)
    test_url1 = 'http://wantit.real-seller.com/api/wantit_api.php?api_type=0&request_url=https://realseller-chatbot.run.goorm.io/profile/data2&mb_email='
    url = test_url1 + user_data['email']
    response3 = requests.post(url)
    api_data = json.loads(response3.text)
    if api_data['return_val'] == "Y":
        print("OK")
        result = {
            "status": "SUCCESS",
            "value": user_data, # user_data 를 통째로 넘기면 어떨까?
            "data": {"phone_number": user_data['phone_number'],"mb_email": user_data['email']},
            "message": "회원입니다!\n"
        } # data는 별도로 전달되지 않는것 같음
    else :
        print("NO")
        result = {
            "status": "SUCCESS",
            "value": user_data,
            "data": {"phone_number": user_data['phone_number'],"mb_email": user_data['email']},
            "message": "회원이 아닙니다!\n"
        }
    '''

    return result 


@application.route('/profile/data2',methods=['POST'])
def api_response():
    api_t = request.form['api_type']
    api_v = request.form['return_val']

    data = {"api_type":api_t,"return_val":api_v}
    return json.dumps(data)

@application.route('/profile/info',methods=['POST'])
def user_data():
    response_data = request.get_json()
    user_res = requests.get(response_data['action']['params']['profile'])
    user_data = json.loads(user_res.text)
    print(response_data)
    
    #user_data['email']='ssahn0806@kw.ac.kr'
    
    member_url = f'http://wantit.real-seller.com/api/wantit_api.php?api_type=0&request_url=https://realseller-chatbot.run.goorm.io/profile/data2&mb_email='

    member_url = member_url + user_data['email']
    member_res = requests.post(member_url)
    member_data = json.loads(member_res.text)        
    
    if member_data['return_val'] == 'Y': # 회원        
        input_data = response_data['action']['clientExtra']['data'][0]['extra']
        print(input_data,type(input_data))
        send_url = f'http://wantit.real-seller.com/api/wantit_api.php?api_type=1&request_url=https://realseller-chatbot.run.goorm.io/profile/data2&mb_email='
        send_data = f"{user_data['email']}&maker={input_data['manufacture']}&series={input_data['series']}&model={input_data['model']}&storage={input_data['capacity'].replace('GB','')}&color={input_data['color_num']}&condition={input_data['grade']}&memo={input_data['additional']}"
        
        send_url = send_url + send_data
        send_res = requests.post(send_url)
        send_data = json.loads(send_res.text)
        
        if send_data['return_val'] == 'Y':
            result = {
            "version":"2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text" : "회원이시군요! 문의결과는 회원정보에 등록된 이메일로 2~3일 내에 전송됩니다."
                        }
                    }
                ]
            }
    }
    else :   # 비회원     
        phone_number = user_data['phone_number'].split(' ')[1]
        num_vars = phone_number.split('-')
        print(phone_number)
        
        result = {
            "version":"2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text" : "비회원이시군요?답변에 필요한 정보 입력이 필요합니다."
                        }
                    }
                ],
                "quickReplies":[
                  {"label":"정보 입력하기",
                   "action":"block",
                   "messageText":"정보 입력하기",
                   "blockId":expert_blockItem['go_to_nonmember'],
                   "extra":{"mb_email":user_data['email'],
                            "mb_ph_1": num_vars[0],
                            "mb_ph_2": num_vars[1],
                            "mb_ph_3": num_vars[2],
                            "data": response_data['action']['clientExtra']['data'][0]['extra']}
                  }
                ]
            }
        }
    return result
if __name__ == "__main__" :
    application.run(host='0.0.0.0')
