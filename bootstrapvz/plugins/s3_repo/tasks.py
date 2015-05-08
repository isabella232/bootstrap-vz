import os
import os.path
from shutil import copy

from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tools import log_check_call

class S3InstallPackage(Task):
        description = 'Install a .deb package immediately after debootstrap'
        phase = phases.os_installation
        predecessors = [filesystem.MountSpecials]

        @classmethod
        def run(cls, info):
                import logging
                log = logging.getLogger(__name__ + "_s3_repo")

                log.debug('Building package paths:')
                absolute_package_paths = []
                chrooted_package_paths = []
                for path in info.manifest.plugins['s3_repo']['paths']:
                        pkg_name = os.path.basename(path)
                        package_rel_dst = os.path.join('tmp', pkg_name)
                        package_dst = os.path.join(info.root, package_rel_dst)
                        copy(path, package_dst)
                        absolute_package_paths.append(package_dst)
                        package_path = os.path.join('/', package_rel_dst)
                        chrooted_package_paths.append(package_path)

                log.debug('Chrooted Package paths are: ' + str(chrooted_package_paths))

                env = os.environ.copy()
                env['DEBIAN_FRONTEND'] = 'noninteractive'
                log_check_call(['chroot', info.root,
                                'dpkg', '--install']
                               + chrooted_package_paths,
                               env=env)

                log.debug('Removing package files from chrooted env: ' +
                          str(absolute_package_paths))
                for path in absolute_package_paths:
                        os.remove(path)
