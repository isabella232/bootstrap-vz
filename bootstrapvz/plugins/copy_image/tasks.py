from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.providers.ec2.tasks import ami

class CopyEC2AMIOverRegion(Task):
	description = 'Copy AWS AMI over another regions'
	phase = phases.image_registration
	predecessors = [ami.RegisterAMI]

	@classmethod
	def run(cls, info):
		copy_descpriton = "Copied from %s (%s) %s" % (info.image, info.host['region'], info.ami_name)
		from boto.ec2 import connect_to_region
		for region in info.manifest.plugins['copy_image']['regions']:
			conn = connect_to_region(region,
									aws_access_key_id=info.credentials['access-key'],
			                        aws_secret_access_key=info.credentials['secret-key'])
			conn.copy_image(info.host['region'], info.image,
							name=info.ami_name, description=copy_descpriton)
