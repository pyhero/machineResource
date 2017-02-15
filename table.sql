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
