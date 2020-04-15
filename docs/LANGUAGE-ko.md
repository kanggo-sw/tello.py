# 개요
`Tello.py`는 [DSL](https://www.jetbrains.com/ko-kr/mps/concepts/domain-specific-languages/)을 통한 스크립트 작성을 지원합니다.

이 기능은 SDK 2.0 이상인 `Tello EDU`에서만 사용할 수 있습니다.

## 언어 기능
다음은 사용 가능한 스크립트 명령입니다.
### scan [N]
N개의 Tello 기기를 네트워크에서 찾습니다.
#### example
`scan 2`

### battery_check [VALUE]
모든 Tello 기기의 전원이 제공된 값보다 작으면 스크립트가 자동으로 종료되고 착륙 명령을 전송합니다.
#### example
`battery_check 25`

### correct_ip
Tello `Serial Number`와 할당된 IP 주소를 바인딩합니다. 이렇게 하면 명령을 실행하기 위해 특정 텔로를 지정할 수 있습니다.

### [ID] = [SN]
Tello ID와 `Serial Number`를 바인딩합니다.
> 이 명령은 `correct_ip` 뒤에 있어야 합니다.
#### example
`1=[Serial number of your device]`

### sync [TIME]
전송된 모든 명령을 동기화합니다.
#### example
`sync 10`

### delay [TIME]
`TIME`(초) 만큼 기다립니다. 이 사이에 다른 명령을 수행할 수 없습니다.
#### example
`delay 3`

### [ID] > [COMMAND]
지정된 ID에 명령을 전송합니다. 이 명령은 `Tello SDK`에서 지원하는 명령이어야 합니다.
[여기](#Tello-SDK-Commands)에서 모든 명령을 볼 수 있습니다.
> 와일드카드(*)를 사용하면 모든 기기에 명령을 전송합니다.
#### example
1번 기기에 전송하려면:`1>up 30`

모든 기기에 전송하려면: `*>up 30`

## Tello SDK Commands
[Tello SDK 2.0 User Guide](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)

# 추가 기능
아래의 명령은 `Tello.py`에서 제공하며 다른 라이브러리에서는 사용할 수 없습니다.

## macro [NAME]:
설명보다는 보는게 편합니다..
```
*> up 30
*> down 10
*> right 5
*> left 5

*> up 30
*> down 10
*> right 5
*> left 5
```
이는 다음과 같습니다:
```
macro myMacro:
*> up 30
*> down 10
*> right 5
*> left 5

myMacro
myMacro
```
