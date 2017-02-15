from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1902 import Integer, IpAddress, OctetString
import MySQLdb

DBINFO = {'host': '10.0.202.201',
          'port': 3306,
          'user': 'noc',
          'password': 'ksBtZ1f25cv7',
          'db': 'hx_noc',
          'table': 'hx_resource'
          #grant select,insert,delete,update,create on hx_noc.* to 'noc'@'10.%' identified by 'ksBtZ1f25cv7';
          }

def mysql(sql):
    try:
        conn = MySQLdb.connect(host=DBINFO['host'],
                               user=DBINFO['user'],
                               passwd=DBINFO['password'],
                               port=DBINFO['port'],
                               db=DBINFO['db'],
                               connect_timeout=10
                               )
        conn.set_character_set('utf8')
        cur = conn.cursor()
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        cur.execute(sql)
        conn.commit()
        conn.close()
    except MySQLdb.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        exit(2)

# create table
sql = '''
CREATE TABLE IF NOT EXISTS `hx_resource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(15) NOT NULL,
  `cpu` float(3,2) NOT NULL,
  `memary_free` float(6,2) NOT NULL,
  `memary_total` float(6,2) NOT NULL,
  `disk_free` float(8,2) NOT NULL,
  `disk_total` float(8,2) NOT NULL,
  `disks` text,
  PRIMARY KEY (`id`),
  KEY `ip` (`ip`),
  KEY `inx_mem` (`memary_free`,`memary_total`),
  KEY `inx_disk` (`disk_free`,`disk_total`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''
mysql(sql)

def getSnmp(ip,oid,passwd='vistata'):
    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.CommunityData(passwd),
        cmdgen.UdpTransportTarget((ip, 161)),
        oid
    )
    if errorIndication:
        #print(errorIndication)
        return 0
    else:
        if errorStatus:
            #print('{} @ {}'.format(errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex)-1] or '?'))
            return 0
        else:
            #print(varBinds)
            for name, val in varBinds:
                #print('{} = {}'.format(name.prettyPrint(), val.prettyPrint()))
                if 'OID' in '{}'.format(val.prettyPrint()):
                    return 0
                else:
                    return val

def getInfo(ip):
    Resource = dict()
    # cpu
    CpuRawUser = getSnmp(ip, '1.3.6.1.4.1.2021.11.50.0')
    CpuRawSystem = getSnmp(ip, '1.3.6.1.4.1.2021.11.52.0')
    CpuRawIdle = getSnmp(ip,'1.3.6.1.4.1.2021.11.53.0')
    Total = int(CpuRawUser) + int(CpuRawSystem) + int(CpuRawIdle)
    if Total == 0:
        cpuFree = 0
    else:
        cpuFree = float('{:.2f}'.format(int(CpuRawIdle)/Total))

    Resource['cpuFree'] = cpuFree

    # mem
    memAvailReal = getSnmp(ip, '1.3.6.1.4.1.2021.4.6.0')
    memTotalReal = getSnmp(ip, '1.3.6.1.4.1.2021.4.5.0')
    memBuffer = getSnmp(ip, '1.3.6.1.4.1.2021.4.14.0')
    memCached = getSnmp(ip, '1.3.6.1.4.1.2021.4.15.0')

    memFree = float('{:.2f}'.format((int(memAvailReal) + int(memBuffer) + int(memCached)) / 1024 / 1024))
    memTotal = float('{:.2f}'.format(int(memTotalReal) / 1024 / 1024))

    Resource['memory'] = {'free': memFree, 'total': memTotal}

    # disk
    index = 1
    DiskTotalFree = 0
    DiskTotalTotal = 0
    Disk = dict()
    Disks = ''
    while True:
        dskPath = getSnmp(ip, ('1.3.6.1.4.1.2021.9.1.2.' + str(index)))
        if dskPath:
            dskAvail = getSnmp(ip, ('1.3.6.1.4.1.2021.9.1.7.' + str(index)))
            dskTotal = getSnmp(ip, ('1.3.6.1.4.1.2021.9.1.6.' + str(index)))
            DiskFree = float('{:.2f}'.format(int(dskAvail) / 1024 / 1024))
            DiskTotal = float('{:.2f}'.format(int(dskTotal) / 1024 / 1024))
            Disk['Disk-{}'.format(dskPath)] = {'free': DiskFree, 'total': DiskTotal}
            Disks += "Disk-{}: free={} total={},".format(dskPath,DiskFree,DiskTotal)
            #print('disk-{}: Free: {} Total: {}'.format(dskPath, DiskFree,DiskTotal))
            DiskTotalFree += DiskFree
            DiskTotalTotal += DiskTotal
            index += 1
        else:
            break

    Resource['disks'] = Disk
    Resource['disk'] = {'free': DiskTotalFree, 'total': DiskTotalTotal}

    sql = "insert into {} (ip,cpu,memary_free,memary_total,disk_free,disk_total,disks) VALUES " \
          "('{}',{},{},{},{},{},'{}');".format(DBINFO['table'],
                                           ip,
                                           cpuFree,
                                           memFree,memTotal,
                                           DiskTotalFree,DiskTotalTotal,
                                           Disks
                                           )
    mysql(sql)
    #print(sql)

file = open('./ips.lst')
try:
    ips = file.readlines()
    for ip in ips:
        ip = ''.join(ip).strip('\n')
        print('Do for {}'.format(ip))
        getInfo(ip)
finally:
    file.close()