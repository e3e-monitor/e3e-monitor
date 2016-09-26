/*
 * Copyright 2012-2014 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ch.e3e.gateway.echo;

import static org.junit.Assert.assertEquals;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.test.IntegrationTest;
import org.springframework.boot.test.SpringApplicationConfiguration;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.Configuration;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;

import ch.e3e.gateway.config.E3eGatewayApplication;

@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = { E3eGatewayApplication.class })
@WebAppConfiguration
@IntegrationTest
@DirtiesContext
public class CustomContainerWebSocketsApplicationTests {

	private static Log logger = LogFactory
			.getLog(CustomContainerWebSocketsApplicationTests.class);


	@Test
	public void runAndWait() throws Exception {
		ConfigurableApplicationContext context = SpringApplication.run(
				ClientConfiguration.class, "--spring.main.web_environment=false");
		long count = context.getBean(ClientConfiguration.class).latch.getCount();
		context.close();
//		assertEquals(0, count);
	}

	@Configuration
	static class ClientConfiguration implements CommandLineRunner {

		private final CountDownLatch latch = new CountDownLatch(1);

		@Override
		public void run(String... args) throws Exception {
			logger.info("Waiting for response: latch=" + this.latch.getCount());
			this.latch.await(10, TimeUnit.SECONDS);
			logger.info("Got response: latch=" + this.latch.getCount());
		}

	
	}

}
