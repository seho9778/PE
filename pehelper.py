import streamlit as st
import time
from generate import generate
import asyncio

############### streamlit basic setting  ####################
st.set_page_config(layout='wide')
# session_state 관리
if 'prompts' not in st.session_state:
    st.session_state['prompts'] = []

if 'model_configs' not in st.session_state:
    st.session_state['model_configs'] = []

if 'generation_results' not in st.session_state:
    st.session_state['generation_results'] = []

############### 페이지 디자인 영역 ####################
with open( "style.css", encoding='utf-8-sig' ) as css:
    st.markdown(f"""<style>{css.read()}</style>""", unsafe_allow_html=True)

############### 페이지 상호작용 함수 영역 ##################
# 프롬프트 삭제
def delete_chat(chat_index):
    st.session_state['prompts'] = st.session_state['prompts'][:chat_index] \
        + st.session_state['prompts'][chat_index+1 : ]

@st.dialog("프롬프트 수정")
def modify_chat(chat_index) : 
    now_prompt = st.session_state['prompts'][chat_index][-1]
    now_cate = st.session_state['prompts'][chat_index][0]
    
    # 프롬프트 수정
    modified_prompt = st.text_input(label='프롬프트수정', value=now_prompt, label_visibility='collapsed', )
    finish_modify = st.button(label ="Modify", key=f'modify-dialog')
    if finish_modify : 
        st.session_state['prompts'][chat_index] = (now_cate, modified_prompt)
        st.rerun()

# 모델 추가
def add_model_config() : 
    model_name= st.session_state.add_model
    model_configs = {
        "model_name"  : model_name,
        "temperature" : 1.0,
        "maximum_token" : 4096,
        "top_p" : 1.0
    }
    if model_name != '선택' : 
        st.session_state['model_configs'].append(model_configs)

# 모델 삭제
def delete_model(model_index) : 
    st.session_state['model_configs'] = st.session_state['model_configs'][:model_index] \
        + st.session_state['model_configs'][model_index+1 : ]
    
# temperature 변경
def change_temperature(model_index):
    st.session_state['model_configs'][model_index]["temperature"] = st.session_state[f'temperature{model_index}']

# temperature 변경
def change_top_p(model_index):
    st.session_state['model_configs'][model_index]["top_p"] = st.session_state[f'top_p{model_index}']

############### 페이지 영역 ####################
st.title('Prompt Engineering Helper')

# 페이지 레이아웃 잡기
prompt_setting, config_setting = st.columns([2, 1])

#### PROMPT SETTING AREA #####
# prompt_setting.subheader('프롬프트 세팅')
# 프롬프트 세팅 -> 사이드 바로 빼는 것도 고려?
# 1. System Prompt
system_prompt = prompt_setting.text_area(label = '시스템프롬프트', placeholder="System Prompt")


# 2. 추가한 프롬프트 보여주기
for ind, prompt in enumerate(st.session_state['prompts']) : 
    cate, text = prompt
    prompt_container = prompt_setting.container(border=True)
    with prompt_container : 
        prompt_container.write(f'<p>{cate}</p>', unsafe_allow_html=True)
        prompt_container.write(f'<span> {text} </span>', unsafe_allow_html=True)
        
        # del_button, mod_button = prompt_container.columns([1, 1], gap="small")
        delete = prompt_container.button("❌ Delete", key=f'del{ind}', on_click=delete_chat, args=(ind, ))
        modify =prompt_container.button("✏️ Modify", key=f'mod{ind}', on_click=modify_chat, args=(ind, ))

## 프롬프트 종류에 따른 입력
# prompt_category, _ = prompt_setting.columns([1, 1.5], )
# category = prompt_category.selectbox(label = "입력카테고리", 
#                                      options = ["human", "ai"], 
#                                      label_visibility = 'collapsed')

prompt_category, add_prompt, add_button = prompt_setting.columns([2, 5, 1])
category = prompt_category.selectbox(label = "입력카테고리", 
                                     options = ["human", "ai"], 
                                     label_visibility = 'collapsed')
add_prompt = add_prompt.text_input(label = '추가프롬프트', 
                                placeholder="Prompt",
                                label_visibility = 'collapsed',
                                )
add_button = add_button.button("Add", type="primary")
if add_button and add_prompt : 
    st.session_state['prompts'].append((category, add_prompt))
    st.rerun()


#### CONFIG SETTING AREA #####
# config_setting.subheader('Config 세팅')
# 모델 추가 selectbox
models = ['선택', 'gpt-4o', 'gpt-4o-mini','gpt-3.5-turbo', 
          'claude-3-5-sonnet-20240620', 'claude-3-opus-20240229',
          'gemini-1.5-flash', 'gemini-1.5-pro']
add_model = config_setting.selectbox(label='모델추가', 
                                     options=models,
                                     key='add_model',
                                     on_change=add_model_config
                                     )

# config expanders
for ind, config in enumerate(st.session_state['model_configs']) : 
    model_name = config['model_name']
    config_expander = config_setting.expander(label=model_name)
    # temperature 세팅
    config_expander.slider(label='temperature', 
                           min_value=0.0, 
                           max_value=2.0, 
                           step=0.01, 
                           value=config['temperature'],
                           key=f'temperature{ind}',
                           on_change=change_temperature,
                           args=(ind,)
                           )
    # top_p 세팅
    config_expander.slider(label='top_p', 
                           min_value=0.0, 
                           max_value=1.0, 
                           step=0.01, 
                           value=config['top_p'],
                           key=f'top_p{ind}',
                           on_change=change_top_p,
                           args=(ind,)
                           )
    config_expander.button('Delete', key=f'model_delete{ind}', on_click=delete_model, args=(ind,))

# general setting
choiced_model = [x['model_name'] for x in st.session_state['model_configs']]
openai_check = True if len([name for name in choiced_model if 'gpt' in name]) else False
claude_check = True if len([name for name in choiced_model if 'claude' in name]) else False
gemini_check = True if len([name for name in choiced_model if 'gemini' in name]) else False
openai_api_key = "pehelper"
claude_api_key = "pehelper"
gemini_api_key = "pehelper"

key_input = config_setting.container()
with key_input :
    if openai_check : 
        openai_api_key = key_input.text_input(label="OPENAI_API_KEY", type="password")
    if claude_check : 
        claude_api_key = key_input.text_input(label="ANTHROPIC_API_KEY", type="password")
    if gemini_check : 
        gemini_api_key = key_input.text_input(label="GEMINI_API_KEY", type="password")
    generate_times = key_input.number_input(label="생성 시도 수", min_value=1, max_value=10, value=1, step=1, key="generate_times")
    gen_button = key_input.button("GENERATE", type='primary')
    # key_forms.form_submit_button(label="RUN")

Error = ""
# ERROR CHECK
if gen_button : 
    # 대화 내용이 있는지
    if not st.session_state['prompts'] : 
        Error = config_setting.error('프롬프트를 입력해주세요.')
    # 모델을 설정했는지
    elif not st.session_state['model_configs'] : 
        Error = config_setting.error('생성을 위한 모델을 선택해주세요.')
    # API key 입력이 잘 됐는지
    elif not openai_api_key : 
        Error = config_setting.error('API KEY를 입력해주세요.')
    elif not claude_api_key : 
        Error = config_setting.error('API KEY를 입력해주세요.')
    elif not gemini_api_key : 
        Error = config_setting.error('API KEY를 입력해주세요.')

    # api key 연결
    for config in st.session_state['model_configs'] : 
        model_name = config['model_name']
        if 'gpt' in model_name : 
            config['api_key'] = openai_api_key
        if 'claude' in model_name : 
            config['api_key'] = claude_api_key
        if 'gemini' in model_name : 
            config['api_key'] = gemini_api_key
    # 중복제거
    # st.session_state['model_configs'] = list(set(st.session_state['model_configs']))

    # system prompt 연결
    if system_prompt :
        st.session_state['prompts'] = [('system', system_prompt)] + st.session_state['prompts']

    if not Error : 
        with config_setting : 
            with st.spinner('텍스트 생성 중...') : 
                try : 
                    # 비동기 루프 실행
                    # async def generate(configs = [], generate_times=1):
                    results = asyncio.run(generate(st.session_state['model_configs'], 
                                                   generate_times=1, 
                                                   chatprompt=st.session_state['prompts']))
                    # 결과페이지로 이동
                    st.switch_page("pages/results.py")
                except Exception as e : 
                    st.error(e)
# print(st.session_state['prompts'])

# 결과 화면
# 아무것도 없으면 아이콘

# config 세팅화면