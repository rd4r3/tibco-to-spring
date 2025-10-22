```bash
#!/bin/bash

# Logging function
log() {
    echo "[INFO] $1"
}

# Create directory structure
log "Creating directory structure..."
mkdir -p fintech-transaction-processor/src/{main,test}/{java/com/fintech,resources/{static,templates}}
mkdir -p fintech-transaction-processor/src/{main,test}/resources/{config,drools}

# Create package directories
mkdir -p fintech-transaction-processor/src/main/java/com/fintech/{config,controller,service,repository,model,exception,listener,publisher,batch,util}
mkdir -p fintech-transaction-processor/src/test/java/com/fintech/{controller,service,repository,listener,publisher,batch,util}

# Create resource directories
mkdir -p fintech-transaction-processor/src/main/resources/{schemas,transformations,logs}

# Create pom.xml
log "Creating pom.xml..."
cat << 'EOF' > fintech-transaction-processor/pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.5.0</version>
        <relativePath/>
    </parent>

    <groupId>com.fintech</groupId>
    <artifactId>fintech-transaction-processor</artifactId>
    <version>1.0.0</version>
    <name>Fintech Transaction Processor</name>
    <description>Spring Boot application for processing fintech transactions</description>

    <properties>
        <java.version>25</java.version>
        <drools.version>8.50.0.Final</drools.version>
        <spring-cloud-gcp.version>4.6.0</spring-cloud-gcp.version>
        <lombok.version>1.18.30</lombok.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-batch</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-mail</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Drools -->
        <dependency>
            <groupId>org.drools</groupId>
            <artifactId>drools-core</artifactId>
            <version>${drools.version}</version>
        </dependency>
        <dependency>
            <groupId>org.drools</groupId>
            <artifactId>drools-compiler</artifactId>
            <version>${drools.version}</version>
        </dependency>

        <!-- Google Cloud Pub/Sub -->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-gcp-starter-pubsub</artifactId>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>${lombok.version}</version>
            <optional>true</optional>
        </dependency>

        <!-- Database -->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.batch</groupId>
            <artifactId>spring-batch-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

    <repositories>
        <repository>
            <id>spring-milestones</id>
            <name>Spring Milestones</name>
            <url>https://repo.spring.io/milestone</url>
        </repository>
    </repositories>
</project>
EOF

# Create application.properties
log "Creating application.properties..."
cat << 'EOF' > fintech-transaction-processor/src/main/resources/application.properties
# Server Configuration
server.port=8080

# Database Configuration
spring.datasource.url=jdbc:mysql://localhost:3306/fintech_db
spring.datasource.username=fintech_user
spring.datasource.password=securepassword123
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA/Hibernate Configuration
spring.jpa.show-sql=true
spring.jpa.hibernate.ddl-auto=update
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL8Dialect

# Logging Configuration
logging.level.root=INFO
logging.level.com.fintech=DEBUG
logging.file.name=logs/transaction.log

# Email Configuration
spring.mail.host=smtp.fintech.com
spring.mail.port=587
spring.mail.username=support@fintech.com
spring.mail.password=emailpassword123

# Google Cloud Pub/Sub Configuration
spring.cloud.gcp.project-id=your-project-id
spring.cloud.gcp.credentials.location=classpath:service-account.json

# Batch Configuration
spring.batch.job.enabled=false
EOF

# Create Drools rules
log "Creating Drools rules..."
cat << 'EOF' > fintech-transaction-processor/src/main/resources/drools/transaction-rules.drl
package com.fintech.rules

import com.fintech.model.Transaction

rule "HighValueTransaction"
    when
        $transaction : Transaction(amount > 10000)
    then
        $transaction.setProcessingStatus("HighValueQueue");
        System.out.println("High value transaction detected: " + $transaction.getId());
end

rule "FraudReviewTransaction"
    when
        $transaction : Transaction(riskScore > 0.75)
    then
        $transaction.setProcessingStatus("FraudReview");
        System.out.println("High risk transaction detected: " + $transaction.getId());
end

rule "UsdTransaction"
    when
        $transaction : Transaction(currency == "USD")
    then
        $transaction.setProcessingStatus("UsdProcessor");
        System.out.println("USD transaction detected: " + $transaction.getId());
end

rule "StandardTransaction"
    when
        $transaction : Transaction()
    then
        $transaction.setProcessingStatus("StandardQueue");
        System.out.println("Standard transaction detected: " + $transaction.getId());
end
EOF

# Create Java codebase
log "Creating Java codebase..."

# Create AppConfig.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/config/AppConfig.java
package com.fintech.config;

import org.kie.api.KieServices;
import org.kie.api.runtime.KieContainer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    @Bean
    public KieContainer kieContainer() {
        KieServices kieServices = KieServices.Factory.get();
        return kieServices.getKieClasspathContainer();
    }
}
EOF

# Create DatabaseConfig.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/config/DatabaseConfig.java
package com.fintech.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
public class DatabaseConfig {

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource")
    public DataSource dataSource() {
        return DataSourceBuilder.create().build();
    }
}
EOF

# Create PubSubConfig.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/config/PubSubConfig.java
package com.fintech.config;

import com.google.cloud.spring.pubsub.core.PubSubTemplate;
import com.google.cloud.spring.pubsub.integration.AckMode;
import com.google.cloud.spring.pubsub.integration.inbound.PubSubInboundChannelAdapter;
import com.google.cloud.spring.pubsub.support.BasicAcknowledgeablePubsubMessage;
import com.google.cloud.spring.pubsub.support.GcpPubSubHeaders;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.integration.channel.DirectChannel;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.MessageHandler;

@Configuration
public class PubSubConfig {

    @Bean
    public MessageChannel pubsubInputChannel() {
        return new DirectChannel();
    }

    @Bean
    public PubSubInboundChannelAdapter messageChannelAdapter(
            @Qualifier("pubsubInputChannel") MessageChannel inputChannel,
            PubSubTemplate pubSubTemplate) {
        PubSubInboundChannelAdapter adapter =
                new PubSubInboundChannelAdapter(pubSubTemplate, "transaction-subscription");
        adapter.setOutputChannel(inputChannel);
        adapter.setAckMode(AckMode.MANUAL);
        adapter.setPayloadType(String.class);
        return adapter;
    }

    @Bean
    @ServiceActivator(inputChannel = "pubsubInputChannel")
    public MessageHandler messageReceiver() {
        return message -> {
            BasicAcknowledgeablePubsubMessage originalMessage =
                    message.getHeaders().get(GcpPubSubHeaders.ORIGINAL_MESSAGE, BasicAcknowledgeablePubsubMessage.class);
            originalMessage.ack();
            // TODO: Process the received message
        };
    }
}
EOF

# Create BatchConfig.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/config/BatchConfig.java
package com.fintech.config;

import com.fintech.model.Transaction;
import com.fintech.repository.TransactionRepository;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.batch.item.ItemReader;
import org.springframework.batch.item.ItemWriter;
import org.springframework.batch.item.data.RepositoryItemReader;
import org.springframework.batch.item.data.builder.RepositoryItemReaderBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.Sort;
import org.springframework.transaction.PlatformTransactionManager;

import java.util.Collections;

@Configuration
@EnableBatchProcessing
public class BatchConfig {

    @Autowired
    private TransactionRepository transactionRepository;

    @Bean
    public ItemReader<Transaction> reader() {
        return new RepositoryItemReaderBuilder<Transaction>()
                .name("transactionReader")
                .repository(transactionRepository)
                .methodName("findAll")
                .sorts(Collections.singletonMap("id", Sort.Direction.ASC))
                .build();
    }

    @Bean
    public ItemProcessor<Transaction, Transaction> processor() {
        return transaction -> {
            // TODO: Implement processing logic
            return transaction;
        };
    }

    @Bean
    public ItemWriter<Transaction> writer() {
        return items -> {
            // TODO: Implement writing logic
        };
    }

    @Bean
    public Step transactionProcessingStep(JobRepository jobRepository,
                                          PlatformTransactionManager transactionManager,
                                          ItemReader<Transaction> reader,
                                          ItemProcessor<Transaction, Transaction> processor,
                                          ItemWriter<Transaction> writer) {
        return new StepBuilder("transactionProcessingStep", jobRepository)
                .<Transaction, Transaction>chunk(10, transactionManager)
                .reader(reader)
                .processor(processor)
                .writer(writer)
                .build();
    }

    @Bean
    public Job transactionProcessingJob(JobRepository jobRepository, Step transactionProcessingStep) {
        return new JobBuilder("transactionProcessingJob", jobRepository)
                .start(transactionProcessingStep)
                .build();
    }
}
EOF

# Create TransactionController.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/controller/TransactionController.java
package com.fintech.controller;

import com.fintech.model.Transaction;
import com.fintech.service.TransactionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/transactions")
public class TransactionController {

    @Autowired
    private TransactionService transactionService;

    @PostMapping
    public ResponseEntity<Transaction> processTransaction(@RequestBody Transaction transaction) {
        Transaction processedTransaction = transactionService.processTransaction(transaction);
        return ResponseEntity.ok(processedTransaction);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Transaction> getTransaction(@PathVariable Long id) {
        Transaction transaction = transactionService.getTransaction(id);
        return ResponseEntity.ok(transaction);
    }
}
EOF

# Create TransactionService.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/service/TransactionService.java
package com.fintech.service;

import com.fintech.model.Transaction;
import com.fintech.repository.TransactionRepository;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class TransactionService {

    @Autowired
    private TransactionRepository transactionRepository;

    @Autowired
    private KieContainer kieContainer;

    public Transaction processTransaction(Transaction transaction) {
        // Validate transaction
        if (!validateTransaction(transaction)) {
            throw new IllegalArgumentException("Invalid transaction");
        }

        // Enrich transaction
        enrichTransaction(transaction);

        // Apply business rules
        applyBusinessRules(transaction);

        // Persist transaction
        return transactionRepository.save(transaction);
    }

    public Transaction getTransaction(Long id) {
        return transactionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Transaction not found"));
    }

    private boolean validateTransaction(Transaction transaction) {
        // TODO: Implement validation logic
        return true;
    }

    private void enrichTransaction(Transaction transaction) {
        // TODO: Implement enrichment logic
    }

    private void applyBusinessRules(Transaction transaction) {
        KieSession kieSession = kieContainer.newKieSession("transactionRulesSession");
        kieSession.insert(transaction);
        kieSession.fireAllRules();
        kieSession.dispose();
    }
}
EOF

# Create PubSubService.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/service/PubSubService.java
package com.fintech.service;

import com.google.cloud.spring.pubsub.core.PubSubTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class PubSubService {

    @Autowired
    private PubSubTemplate pubSubTemplate;

    public void publishMessage(String topic, String message) {
        pubSubTemplate.publish(topic, message);
    }
}
EOF

# Create TransactionRepository.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/repository/TransactionRepository.java
package com.fintech.repository;

import com.fintech.model.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, Long> {
    // Custom query methods can be added here
}
EOF

# Create Transaction.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/model/Transaction.java
package com.fintech.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Entity
public class Transaction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private BigDecimal amount;
    private String currency;
    private LocalDateTime timestamp;
    private String sourceAccount;
    private String destinationAccount;
    private String customerName;
    private String customerId;
    private BigDecimal riskScore;
    private String processingStatus;
}
EOF

# Create GlobalExceptionHandler.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/exception/GlobalExceptionHandler.java
package com.fintech.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;

import java.time.LocalDateTime;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorDetails> handleGlobalException(Exception ex, WebRequest request) {
        ErrorDetails errorDetails = new ErrorDetails(
                LocalDateTime.now(),
                ex.getMessage(),
                request.getDescription(false),
                "INTERNAL_SERVER_ERROR"
        );
        return new ResponseEntity<>(errorDetails, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorDetails> handleIllegalArgumentException(IllegalArgumentException ex, WebRequest request) {
        ErrorDetails errorDetails = new ErrorDetails(
                LocalDateTime.now(),
                ex.getMessage(),
                request.getDescription(false),
                "BAD_REQUEST"
        );
        return new ResponseEntity<>(errorDetails, HttpStatus.BAD_REQUEST);
    }
}
EOF

# Create ErrorDetails.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/exception/ErrorDetails.java
package com.fintech.exception;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class ErrorDetails {
    private LocalDateTime timestamp;
    private String message;
    private String details;
    private String errorCode;
}
EOF

# Create TransactionListener.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/listener/TransactionListener.java
package com.fintech.listener;

import com.fintech.service.TransactionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.gcp.pubsub.support.BasicAcknowledgeablePubsubMessage;
import org.springframework.cloud.gcp.pubsub.support.GcpPubSubHeaders;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.messaging.Message;
import org.springframework.stereotype.Component;

@Component
public class TransactionListener {

    @Autowired
    private TransactionService transactionService;

    @ServiceActivator(inputChannel = "pubsubInputChannel")
    public void processMessage(Message<String> message) {
        BasicAcknowledgeablePubsubMessage originalMessage =
                message.getHeaders().get(GcpPubSubHeaders.ORIGINAL_MESSAGE, BasicAcknowledgeablePubsubMessage.class);

        try {
            String payload = message.getPayload();
            // TODO: Process the payload and call transactionService.processTransaction
            originalMessage.ack();
        } catch (Exception e) {
            originalMessage.nack();
            // TODO: Handle error appropriately
        }
    }
}
EOF

# Create TransactionPublisher.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/publisher/TransactionPublisher.java
package com.fintech.publisher;

import com.fintech.service.PubSubService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class TransactionPublisher {

    @Autowired
    private PubSubService pubSubService;

    public void publishTransaction(String topic, String transactionJson) {
        pubSubService.publishMessage(topic, transactionJson);
    }
}
EOF

# Create TransactionItemProcessor.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/batch/TransactionItemProcessor.java
package com.fintech.batch;

import com.fintech.model.Transaction;
import org.springframework.batch.item.ItemProcessor;

public class TransactionItemProcessor implements ItemProcessor<Transaction, Transaction> {

    @Override
    public Transaction process(Transaction transaction) throws Exception {
        // TODO: Implement processing logic
        return transaction;
    }
}
EOF

# Create LoggingUtil.java
cat << 'EOF' > fintech-transaction-processor/src/main/java/com/fintech/util/LoggingUtil.java
package com.fintech.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggingUtil {

    private static final Logger logger = LoggerFactory.getLogger(LoggingUtil.class);

    public static void logInfo(String message) {
        logger.info(message);
    }

    public static void logError(String message, Throwable throwable) {
        logger.error(message, throwable);
    }
}
EOF

# Create unit tests
log "Creating unit tests..."

# Create TransactionControllerTest.java
cat << 'EOF' > fintech-transaction-processor/src/test/java/com/fintech/controller/TransactionControllerTest.java
package com.fintech.controller;

import com.fintech.model.Transaction;
import com.fintech.service.TransactionService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

class TransactionControllerTest {

    @Mock
    private TransactionService transactionService;

    @InjectMocks
    private TransactionController transactionController;

    private Transaction testTransaction;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);

        testTransaction = new Transaction();
        testTransaction.setId(1L);
        testTransaction.setAmount(new BigDecimal("100.00"));
        testTransaction.setCurrency("USD");
        testTransaction.setTimestamp(LocalDateTime.now());
        testTransaction.setSourceAccount("123456789");
        testTransaction.setDestinationAccount("987654321");
        testTransaction.setCustomerName("John Doe");
        testTransaction.setCustomerId("CUST123");
        testTransaction.setRiskScore(new BigDecimal("0.5"));
        testTransaction.setProcessingStatus("PROCESSED");
    }

    @Test
    void processTransaction_ShouldReturnProcessedTransaction() {
        when(transactionService.processTransaction(testTransaction)).thenReturn(testTransaction);

        ResponseEntity<Transaction> response = transactionController.processTransaction(testTransaction);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(testTransaction, response.getBody());
    }

    @Test
    void getTransaction_ShouldReturnTransaction() {
        when(transactionService.getTransaction(1L)).thenReturn(testTransaction);

        ResponseEntity<Transaction> response = transactionController.getTransaction(1L);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(testTransaction, response.getBody());
    }
}
EOF

# Create TransactionServiceTest.java
cat << 'EOF' > fintech-transaction-processor/src/test/java/com/fintech/service/TransactionServiceTest.java
package com.fintech.service;

import com.fintech.model.Transaction;
import com.fintech.repository.TransactionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

class TransactionServiceTest {

    @Mock
    private TransactionRepository transactionRepository;

    @InjectMocks
    private TransactionService transactionService;

    private Transaction testTransaction;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);

        testTransaction = new Transaction();
        testTransaction.setId(1L);
        testTransaction.setAmount(new BigDecimal("100.00"));
        testTransaction.setCurrency("USD");
        testTransaction.setTimestamp(LocalDateTime.now());
        testTransaction.setSourceAccount("123456789");
        testTransaction.setDestinationAccount("987654321");
        testTransaction.setCustomerName("John Doe");
        testTransaction.setCustomerId("CUST123");
        testTransaction.setRiskScore(new BigDecimal("0.5"));
        testTransaction.setProcessingStatus("PROCESSED");
    }

    @Test
    void processTransaction_ShouldReturnProcessedTransaction() {
        when(transactionRepository.save(testTransaction)).thenReturn(testTransaction);

        Transaction result = transactionService.processTransaction(testTransaction);

        assertEquals(testTransaction, result);
    }

    @Test
    void getTransaction_ShouldReturnTransaction() {
        when(transactionRepository.findById(1L)).thenReturn(Optional.of(testTransaction));

        Transaction result = transactionService.getTransaction(1L);

        assertEquals(testTransaction, result);
    }

    @Test
    void getTransaction_ShouldThrowExceptionWhenNotFound() {
        when(transactionRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(RuntimeException.class, () -> transactionService.getTransaction(1L));
    }
}
EOF

# Create TransactionRepositoryTest.java
cat << 'EOF' > fintech-transaction-processor/src/test/java/com/fintech/repository/TransactionRepositoryTest.java
package com.fintech.repository;

import com.fintech.model.Transaction;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@DataJpaTest
class TransactionRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private TransactionRepository transactionRepository;

    @Test
    void whenFindById_thenReturnTransaction() {
        // given
        Transaction testTransaction = new Transaction();
        testTransaction.setAmount(new BigDecimal("100.00"));
        testTransaction.setCurrency("USD");
        testTransaction.setTimestamp(LocalDateTime.now());
        testTransaction.setSourceAccount("123456789");
        testTransaction.setDestinationAccount("987654321");
        testTransaction.setCustomerName("John Doe");
        testTransaction.setCustomerId("CUST123");
        testTransaction.setRiskScore(new BigDecimal("0.5"));
        testTransaction.setProcessingStatus("PROCESSED");

        entityManager.persist(testTransaction);
        entityManager.flush();

        // when
        Optional<Transaction> found = transactionRepository.findById(testTransaction.getId());

        // then
        assertTrue(found.isPresent());
        assertEquals(testTransaction.getId(), found.get().getId());
    }
}
EOF

# Create TransactionListenerTest.java
cat << 'EOF' > fintech-transaction-processor/src/test/java/com/fintech/listener/TransactionListenerTest.java
package com.fintech.listener;

import com.fintech.service.TransactionService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.cloud.gcp.pubsub.support.BasicAcknowledgeablePubsubMessage;
import org.springframework.cloud.gcp.pubsub.support.GcpPubSubHeaders;
import org.springframework.messaging.Message;
import org.springframework.messaging.support.MessageBuilder;

import static org.mockito.Mockito.*;

class TransactionListenerTest {

    @Mock
    private TransactionService transactionService;

    @Mock
    private BasicAcknowledgeablePubsubMessage acknowledgeablePubsubMessage;

    @InjectMocks
    private TransactionListener transactionListener;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void processMessage_ShouldAcknowledgeMessage() {
        String testPayload = "{\"id\":1,\"amount\":100.00,\"currency\":\"USD\"}";

        Message<String> message = MessageBuilder.withPayload(testPayload)
                .setHeader(GcpPubSubHeaders.ORIGINAL_MESSAGE, acknowledgeablePubsubMessage)
                .build();

        transactionListener.processMessage(message);

        verify(acknowledgeablePubsubMessage, times(1)).ack();
    }

    @Test
    void processMessage_ShouldNackMessageOnException() {
        String testPayload = "invalid json";

        Message<String> message = MessageBuilder.withPayload(testPayload)
                .setHeader(GcpPubSubHeaders.ORIGINAL_MESSAGE, acknowledgeablePubsubMessage)
                .build();

        transactionListener.processMessage(message);

        verify(acknowledgeablePubsubMessage, times(1)).nack();
    }
}
EOF

# Create TransactionPublisherTest.java
cat << 'EOF' > fintech-transaction-processor/src/test/java/com/fintech/publisher/TransactionPublisherTest.java
package com.fintech.publisher;

import com.fintech.service.PubSubService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static org.mockito.Mockito.verify;

class TransactionPublisherTest {

    @Mock
    private PubSubService pubSubService;

    @InjectMocks
    private TransactionPublisher transactionPublisher;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void publishTransaction_ShouldCallPubSubService() {
        String testTopic = "test-topic";
        String testTransactionJson = "{\"id\":1,\"amount\":100.00,\"currency\":\"USD\"}";

        transactionPublisher.publishTransaction(testTopic, testTransactionJson);

        verify(pubSubService).publishMessage(testTopic, testTransactionJson);
    }
}
EOF

# Create TransactionItemProcessorTest.java
cat << 'EOF' > fintech-transaction-processor/src/test/java/com/fintech/batch/TransactionItemProcessorTest.java
package com.fintech.batch;

import com.fintech.model.Transaction;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.assertEquals;

class TransactionItemProcessorTest {

    private TransactionItemProcessor transactionItemProcessor;
    private Transaction testTransaction;

    @BeforeEach
    void setUp() {
        transactionItemProcessor = new TransactionItemProcessor();

        testTransaction = new Transaction();
        testTransaction.setId(1L);
        testTransaction.setAmount(new BigDecimal("100.00"));
        testTransaction.setCurrency("USD");
        testTransaction.setTimestamp(LocalDateTime.now());
        testTransaction.setSourceAccount("123456789");
        testTransaction.setDestinationAccount("987654321");
        testTransaction.setCustomerName("John Doe");
        testTransaction.setCustomerId("CUST123");
        testTransaction.setRiskScore(new BigDecimal("0.5"));
        testTransaction.setProcessingStatus("PROCESSED");
    }

    @Test
    void process_ShouldReturnProcessedTransaction() throws Exception {
        Transaction result = transactionItemProcessor.process(testTransaction);

        assertEquals(testTransaction, result);
        // TODO: Add more specific assertions based on your processing logic
    }
}
EOF

# Create LoggingUtilTest.java
cat << 'EOF' > fintech-transaction-processor/src/test/java/com/fintech/util/LoggingUtilTest.java
package com.fintech.util;

import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static org.mockito.Mockito.*;

class LoggingUtilTest {

    @Test
    void logInfo_ShouldLogMessage() {
        Logger loggerMock = mock(Logger.class);
        when(LoggerFactory.getLogger(LoggingUtil.class)).thenReturn(loggerMock);

        String testMessage = "Test info message";
        LoggingUtil.logInfo(testMessage);

        verify(loggerMock).info(testMessage);
    }

    @Test
    void logError_ShouldLogMessageAndException() {
        Logger loggerMock = mock(Logger.class);
        when(LoggerFactory.getLogger(LoggingUtil.class)).thenReturn(loggerMock);

        String testMessage = "Test error message";
        Exception testException = new Exception("Test exception");

        LoggingUtil.logError(testMessage, testException);

        verify(loggerMock).error(testMessage, testException);
    }
}
EOF

# Build and run the application
log "Building and running the application..."
cd fintech-transaction-processor
mvn clean compile
mvn test
mvn package
java -jar target/fintech-transaction-processor-1.0.0.jar

log "Setup and compilation complete."
```