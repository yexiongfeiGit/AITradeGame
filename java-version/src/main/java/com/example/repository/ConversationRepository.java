package com.example.repository;

import com.example.entity.Conversation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ConversationRepository extends JpaRepository<Conversation, Long> {
    List<Conversation> findByModelIdOrderByTimestampDesc(Long modelId);
    
    List<Conversation> findByModelIdOrderByTimestampDesc(Long modelId, org.springframework.data.domain.Pageable pageable);
    
    @Modifying
    @Query("DELETE FROM Conversation c WHERE c.modelId = :modelId")
    void deleteByModelId(@Param("modelId") Long modelId);
}