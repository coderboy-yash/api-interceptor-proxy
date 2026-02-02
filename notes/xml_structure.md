## minimal traffic.xml file structure
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<TRAFFICML_REALTIME xmlns="http://traffic.nokia.com/trafficml-flow-3.2" MAP_VERSION="202504" MAP_DVN="25131" TMC_TABLE_VERSION="18.0" CREATED_TIMESTAMP="2026-01-29T08:38:13Z" VERSION="3.2.2" UNITS="metric">
    <FEATURES>
        <FEATURE>LANES</FEATURE>
        <FEATURE>FORM_OF_WAY</FEATURE>
        <FEATURE>EXPRESS</FEATURE>
        <FEATURE>OPEN_LR</FEATURE>
        <FEATURE>DLR_AGGREGATION</FEATURE>
        <FEATURE>HOV</FEATURE>
    </FEATURES>
    <RWS TY="TMC" MAP_VERSION="202504" MAP_DVN="25131" EBU_COUNTRY_CODE="5" EXTENDED_COUNTRY_CODE="F2" TABLE_ID="2">
        <RW LI="502-00333" DE="4th Signal Hill Avenue" PBT="2026-01-29T08:38:13Z" mid="482d2489-ce44-4140-90f9-2177963c5b4a"> 
            <FIS>
                <FI>
                    <TMC PC="336" DE="Sewri/Boat Hard Road" QD="+" LE="0.05673"/>
                    <TPEGOpenLRBase64>CCgBEAAkIzPN9w1/OgAJBQQDA60ACgQDA38A/5f/yAAJBQQDAysAMABG</TPEGOpenLRBase64>
                    <CF TY="TR" SP="17.99" SU="17.99" FF="27.0" JF="2.9664" CN="0.72" TS="O"/>
                </FI>
                <FI>
                    <TMC PC="335" DE="Signal Hill Avenue" QD="+" LE="0.29488"/>
                    <TPEGOpenLRBase64>CCkBEAAlJDPN9w1/OgAJBQQDA60ACgUEA4JgAP7l/1kACQUEAwIvADA5AA==</TPEGOpenLRBase64>
                    <CF TY="TR" SP="14.8" SU="14.8" FF="14.0" JF="0.0" CN="0.89" TS="O"/>
                </FI>
                <FI>
                    <TMC PC="334" DE="Sant Savta Marg/Victoria Marg" QD="+" LE="0.28652"/>
                    <TPEGOpenLRBase64>CCkBEAAlJDPNcw1+7AAJBQQDAqsACgUEA4IfAP82/1cACQUEAwIXADAAAA==</TPEGOpenLRBase64>
                    <CF TY="TR" SP="23.4" SU="23.4" FF="32.0" JF="3.58335" CN="0.84" TS="O">
                        <SSS>
                            <SS LE="0.17467" SP="18.89" SU="18.89" FF="32.0" JF="5.56831" TS="O"/>
                            <SS LE="0.11184" SP="37.33" SU="37.33" FF="32.0" JF="0.0" TS="O"/>
                        </SSS>
                    </CF>
                </FI>
            </FIS>
        </RW>
    </RWS>
    <RWS TY="SHP" MAP_VERSION="202504" MAP_DVN="25131" EBU_COUNTRY_CODE="5" EXTENDED_COUNTRY_CODE="F2" TABLE_ID="2">
        <RW PBT="2026-01-29T08:34:12Z" mid="8ae470cd-648f-459e-a1a5-ac9374f76437">
            <FIS>
                <FI>
                    <SHP FC="3" LID="1195881742F" LE="0.36023" FW="MD">19.78609,72.76513 19.78605,72.76502 19.78613,72.76409 19.78618,72.76357 19.78621,72.76332 19.78626,72.76305 19.78636,72.76262 19.78645,72.76228 19.78655,72.76175</SHP>
                    <SHP FC="3" LID="1195881743F" LE="0.08798" FW="MD">19.78655,72.76175 19.78661,72.76137 19.78667,72.76092</SHP>
                    <SHP FC="3" LID="1195881741F" LE="0.07506" FW="MD">19.78667,72.76092 19.78676,72.76021</SHP>
                    <SHP FC="3" LID="1360820957F" LE="0.21341" FW="MD">19.78676,72.76021 19.78682,72.75964 19.78688,72.75871 19.78691,72.75818</SHP>
                    <SHP FC="3" LID="1360820958F" LE="0.02307" FW="MD">19.78691,72.75818 19.78692,72.75796</SHP>
                    <TPEGOpenLRBase64>CCkBEAAlJDO+fQ4R8wAJBQQCArgACgUEAoV3AP0zAFMACQUEAgJCADAAAA==</TPEGOpenLRBase64>
                    <CF TY="TR" SP="24.58" SU="24.58" FF="44.0" JF="6.01977" CN="0.93" TS="O"/>
                </FI>
            </FIS>
        </RW>
    <RWS>
```