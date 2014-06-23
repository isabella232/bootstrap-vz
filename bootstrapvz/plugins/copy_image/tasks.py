from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.providers.ec2.tasks import ami

from time import sleep

class CopyEC2AMIOverRegion(Task):
	description = 'Copy AWS AMI over another regions'
	phase = phases.image_registration
	predecessors = [ami.RegisterAMI]

	@classmethod
	def run(cls, info):
		copy_descpriton = "Copied from %s (%s) %s" % (
			info.image,
			info.host['region'],
			info.ami_name
		)
		from boto.ec2 import connect_to_region
		ami_list = []
		for region in info.manifest.plugins['copy_image']['regions']:
			conn = connect_to_region(
				region,
				aws_access_key_id=info.credentials['access-key'],
				aws_secret_access_key=info.credentials['secret-key'])
                        t = conn.copy_image(
                                info.host['region'], info.image,
                                name=info.ami_name, description=copy_descpriton)

			ami_list.append(
                                (region, t.image_id))
		if info.manifest.plugins['copy_image']['block']:
			state = False
			while not state:
				# AMI copy takes 5~20 minutes
				sleep(150)
				ami_state = []
				for ami_data in ami_list:
					conn = connect_to_region(
						ami_data[0],
						aws_access_key_id=info.credentials['access-key'],
						aws_secret_access_key=info.credentials['secret-key'])

					ami_state.extend(conn.get_all_images(
						image_ids=[ami_data[1]])
					)

				state = reduce(
					lambda x, y: x and y,
					map(lambda x: x.state == 'available', ami_state)
				)
