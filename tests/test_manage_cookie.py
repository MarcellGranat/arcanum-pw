import pytest
import json
import manage_cookie
import pytest
import aiofiles

@pytest.mark.asyncio
async def test_marci():
    with open("cookies/marcigranat.json", "r") as f:
        cookie = json.loads(f.read())
    name = await manage_cookie.logged_in_as(cookie)
    assert name  == "marcigranat@elte.hu"

@pytest.mark.asyncio
async def test_aycopf():
    cookie = await manage_cookie.read_cookie("AYCOPF")
    name = await manage_cookie.logged_in_as(cookie)
    assert name  == "AYCOPF@instructor.metropolitan.hu"

@pytest.mark.asyncio
async def test_password():
    async with aiofiles.open(".arcanum_secrets", "r") as f:
        userdata = (await f.read()).split("\n")
        uni = userdata[0].strip()
        username = userdata[1].strip()
        password = userdata[2].strip()
    cookie = await manage_cookie.cookie_from_password(username, password, uni, slow_mo=1000)
    name = await manage_cookie.logged_in_as(cookie)
    assert name  == "marcigranat@elte.hu"


@pytest.mark.asyncio
async def test_logged_in_as():
    with open("tests/test_cookies/marcigranat.json", "r") as f:
        cookie = json.loads(f.read())
    name = await manage_cookie.logged_in_as(cookie)
    assert name  == "marcigranat@elte.hu"

def test_logged_in_as_expired():
    with pytest.raises(ValueError, match="Cookie has expired"):
        manage_cookie.logged_in_as(None)

def test_corrupt_cookies():
    with open("tests/test_cookies/corrupt.json", "r") as f:
        cookie = json.loads(f.read())
    with pytest.raises(ValueError, match="Cookie is not in valid format"):
        manage_cookie.logged_in_as(cookie)

def test_cookie_folder():
    manage_cookie.set_cookie_folder("tests/test_cookies/")
    assert "corrupt" in list(manage_cookie.generate_usernames())