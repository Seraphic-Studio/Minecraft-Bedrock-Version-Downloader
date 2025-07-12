import uuid
import asyncio
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from typing import List, Optional
import aiohttp


class WUProtocol:
    
    DEFAULT_URL = "https://fe3.delivery.mp.microsoft.com/ClientWebService/client.asmx"
    SECURED_URL = "https://fe3.delivery.mp.microsoft.com/ClientWebService/client.asmx/secured"
    
    NAMESPACES = {
        'soap': 'http://www.w3.org/2003/05/soap-envelope',
        'addressing': 'http://www.w3.org/2005/08/addressing',
        'secext': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
        'secutil': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd',
        'wuws': 'http://schemas.microsoft.com/msus/2014/10/WindowsUpdateAuthorization',
        'wuclient': 'http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService'
    }
    
    def __init__(self):
        self.msa_user_token = None
        
    def set_msa_user_token(self, token: str):
        self.msa_user_token = token
        
    def build_wu_tickets(self) -> ET.Element:
        tickets = ET.Element("{%s}WindowsUpdateTicketsToken" % self.NAMESPACES['wuws'])
        tickets.set("{%s}id" % self.NAMESPACES['secutil'], "ClientMSA")
        tickets.set("{%s}wsu" % ET._namespace_map.get('xmlns', 'xmlns'), self.NAMESPACES['secutil'])
        tickets.set("{%s}wuws" % ET._namespace_map.get('xmlns', 'xmlns'), self.NAMESPACES['wuws'])
        
        if self.msa_user_token:
            ticket_type = ET.SubElement(tickets, "TicketType")
            ticket_type.set("Name", "MSA")
            ticket_type.set("Version", "1.0")
            ticket_type.set("Policy", "MBI_SSL")
            user_elem = ET.SubElement(ticket_type, "User")
            user_elem.text = self.msa_user_token
            
        aad_ticket = ET.SubElement(tickets, "TicketType")
        aad_ticket.set("Name", "AAD")
        aad_ticket.set("Version", "1.0")
        aad_ticket.set("Policy", "MBI_SSL")
        aad_ticket.text = ""
        
        return tickets
        
    def build_header(self, url: str, method_name: str) -> ET.Element:
        now = datetime.utcnow()
        expires = now + timedelta(minutes=5)
        
        header = ET.Element("{%s}Header" % self.NAMESPACES['soap'])
        
        action = ET.SubElement(header, "{%s}Action" % self.NAMESPACES['addressing'])
        action.set("{%s}mustUnderstand" % self.NAMESPACES['soap'], "1")
        action.text = f"http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService/{method_name}"
        
        message_id = ET.SubElement(header, "{%s}MessageID" % self.NAMESPACES['addressing'])
        message_id.text = f"urn:uuid:{uuid.uuid4()}"
        
        to = ET.SubElement(header, "{%s}To" % self.NAMESPACES['addressing'])
        to.set("{%s}mustUnderstand" % self.NAMESPACES['soap'], "1")
        to.text = url
        
        security = ET.SubElement(header, "{%s}Security" % self.NAMESPACES['secext'])
        security.set("{%s}mustUnderstand" % self.NAMESPACES['soap'], "1")
        
        timestamp = ET.SubElement(security, "{%s}Timestamp" % self.NAMESPACES['secutil'])
        created = ET.SubElement(timestamp, "{%s}Created" % self.NAMESPACES['secutil'])
        created.text = now.isoformat() + "Z"
        expires_elem = ET.SubElement(timestamp, "{%s}Expires" % self.NAMESPACES['secutil'])
        expires_elem.text = expires.isoformat() + "Z"
        
        security.append(self.build_wu_tickets())
        
        return header
        
    def get_download_url(self) -> str:
        return self.SECURED_URL
        
    def build_download_request(self, update_identity: str, revision_number: str) -> str:
        envelope = ET.Element("{%s}Envelope" % self.NAMESPACES['soap'])
        envelope.set("{%s}a" % ET._namespace_map.get('xmlns', 'xmlns'), self.NAMESPACES['addressing'])
        envelope.set("{%s}s" % ET._namespace_map.get('xmlns', 'xmlns'), self.NAMESPACES['soap'])
        
        envelope.append(self.build_header(self.get_download_url(), "GetExtendedUpdateInfo2"))
        
        body = ET.SubElement(envelope, "{%s}Body" % self.NAMESPACES['soap'])
        get_extended_update_info = ET.SubElement(body, "{%s}GetExtendedUpdateInfo2" % self.NAMESPACES['wuclient'])
        
        update_ids = ET.SubElement(get_extended_update_info, "{%s}updateIDs" % self.NAMESPACES['wuclient'])
        update_identity_elem = ET.SubElement(update_ids, "{%s}UpdateIdentity" % self.NAMESPACES['wuclient'])
        update_id = ET.SubElement(update_identity_elem, "{%s}UpdateID" % self.NAMESPACES['wuclient'])
        update_id.text = update_identity
        revision_num = ET.SubElement(update_identity_elem, "{%s}RevisionNumber" % self.NAMESPACES['wuclient'])
        revision_num.text = revision_number
        
        info_types = ET.SubElement(get_extended_update_info, "{%s}infoTypes" % self.NAMESPACES['wuclient'])
        fragment_type = ET.SubElement(info_types, "{%s}XmlUpdateFragmentType" % self.NAMESPACES['wuclient'])
        fragment_type.text = "FileUrl"
        
        device_attrs = ET.SubElement(get_extended_update_info, "{%s}deviceAttributes" % self.NAMESPACES['wuclient'])
        device_attrs.text = ("E:BranchReadinessLevel=CBB&DchuNvidiaGrfxExists=1&ProcessorIdentifier=Intel64%20Family%206%20Model%2063%20Stepping%202&"
                            "CurrentBranch=rs4_release&DataVer_RS5=1942&FlightRing=Retail&AttrDataVer=57&InstallLanguage=en-US&"
                            "DchuAmdGrfxExists=1&OSUILocale=en-US&InstallationType=Client&FlightingBranchName=&Version_RS5=10&"
                            "UpgEx_RS5=Green&GStatus_RS5=2&OSSkuId=48&App=WU&InstallDate=1529700913&ProcessorManufacturer=GenuineIntel&"
                            "AppVer=10.0.17134.471&OSArchitecture=AMD64&UpdateManagementGroup=2&IsDeviceRetailDemo=0&"
                            "HidOverGattReg=C%3A%5CWINDOWS%5CSystem32%5CDriverStore%5CFileRepository%5Chidbthle.inf_amd64_467f181075371c89%5C"
                            "Microsoft.Bluetooth.Profiles.HidOverGatt.dll&IsFlightingEnabled=0&DchuIntelGrfxExists=1&TelemetryLevel=1&"
                            "DefaultUserRegion=244&DeferFeatureUpdatePeriodInDays=365&Bios=Unknown&WuClientVer=10.0.17134.471&"
                            "PausedFeatureStatus=1&Steam=URL%3Asteam%20protocol&Free=8to16&OSVersion=10.0.17134.472&DeviceFamily=Windows.Desktop")
        
        return ET.tostring(envelope, encoding='unicode')
        
    def extract_download_response_urls(self, response_xml: str) -> List[str]:
        try:
            root = ET.fromstring(response_xml)
            
            result_elem = None
            for elem in root.iter():
                if elem.tag.endswith('GetExtendedUpdateInfo2Result'):
                    result_elem = elem
                    break
                    
            if result_elem is None:
                return []
                
            urls = []
            for elem in result_elem.iter():
                if elem.tag.endswith('Url'):
                    urls.append(elem.text)
                    
            return urls
            
        except ET.ParseError:
            return []
