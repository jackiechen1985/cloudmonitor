use cloudmonitor;

DROP TABLE IF EXISTS `ftpproducers`;
DROP TABLE IF EXISTS `ftps`;
DROP TABLE IF EXISTS `subtasks`;
DROP TABLE IF EXISTS `tasks`;

CREATE TABLE `tasks` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL UNIQUE,
    `type` varchar(32) NOT NULL,
    `interval` int(10) unsigned DEFAULT NULL,
    `initial_delay` int(10) unsigned DEFAULT NULL,
    `module` varchar(512) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `subtasks` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `start_time` varchar(32) NOT NULL,
    `end_time` varchar(32) NOT NULL,
    `status` varchar(16) NOT NULL,
    `description` varchar(1024) DEFAULT NULL,
    `task_id` int(10) unsigned NOT NULL,
    PRIMARY KEY (`id`),
    KEY `task_id` (`task_id`),
    FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ftps` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `host` varchar(16) NOT NULL,
    `name` varchar(255) NOT NULL,
    `size` bigint(20) NOT NULL,
    `mtime` varchar(32) DEFAULT NULL,
    `local_file_path` varchar(1024) NOT NULL,
    `status` varchar(32) NOT NULL,
    `subtask_id` int(10) unsigned NOT NULL,
    PRIMARY KEY (`id`),
    KEY `subtask_id` (`subtask_id`),
    FOREIGN KEY (`subtask_id`) REFERENCES `subtasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ftpproducers` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `time` varchar(32) NOT NULL,
    `subtask_id` int(10) unsigned NOT NULL,
    `ftp_id` int(10) unsigned NOT NULL,
    PRIMARY KEY (`id`),
    KEY `subtask_id` (`subtask_id`),
    FOREIGN KEY (`subtask_id`) REFERENCES `subtasks` (`id`) ON DELETE CASCADE,
    KEY `ftp_id` (`ftp_id`),
    FOREIGN KEY (`ftp_id`) REFERENCES `ftps` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;