package com.astromeric.android.feature.profile

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.BuildConfig
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumEmptyStateCard
import com.astromeric.android.core.ui.PremiumHeroCard

@Composable
fun HelpFaqScreen(
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var searchQuery by rememberSaveable { mutableStateOf("") }
    var expandedQuestion by rememberSaveable { mutableStateOf<String?>(null) }
    val filteredSections = remember(context, searchQuery) {
        filterFaqSections(context, searchQuery)
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = stringResource(R.string.support_help_hero_eyebrow),
            title = stringResource(R.string.support_help_hero_title),
            body = stringResource(R.string.support_help_hero_body),
            chips = listOf(
                stringResource(R.string.support_help_chip_faq),
                stringResource(R.string.support_help_chip_search),
                stringResource(R.string.support_help_chip_support),
            ),
        )

        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            modifier = Modifier.fillMaxWidth(),
            label = { Text(stringResource(R.string.support_help_search_label)) },
            singleLine = true,
        )

        if (filteredSections.isEmpty()) {
            PremiumEmptyStateCard(
                title = stringResource(R.string.support_help_no_results_title, searchQuery),
                message = stringResource(R.string.support_help_no_results_message),
            )
        } else {
            filteredSections.forEach { section ->
                HelpSectionCard(
                    section = section,
                    expandedQuestion = expandedQuestion,
                    onToggle = { question ->
                        expandedQuestion = if (expandedQuestion == question) null else question
                    },
                )
            }
        }

        PremiumContentCard(
            title = stringResource(R.string.support_help_contact_title),
            body = stringResource(R.string.support_help_contact_body),
        ) {
                Button(
                    onClick = {
                        launchSupportEmail(
                            context = context,
                            subject = context.getString(R.string.support_help_email_subject),
                        )
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.support_help_email_button))
                }
        }
    }
}

@Composable
fun UserGuideScreen(
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var expandedSection by rememberSaveable { mutableStateOf<String?>(null) }
    val sections = remember(context) { userGuideSections(context) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = stringResource(R.string.support_guide_hero_eyebrow),
            title = stringResource(R.string.support_guide_hero_title),
            body = stringResource(R.string.support_guide_hero_body),
            chips = listOf(
                stringResource(R.string.support_guide_chip_getting_started),
                stringResource(R.string.support_guide_chip_tools),
                stringResource(R.string.support_guide_chip_privacy),
            ),
        )

        sections.forEach { section ->
            UserGuideSectionCard(
                section = section,
                expanded = expandedSection == section.title,
                onToggle = {
                    expandedSection = if (expandedSection == section.title) null else section.title
                },
            )
        }
    }
}

@Composable
private fun HelpSectionCard(
    section: HelpSectionData,
    expandedQuestion: String?,
    onToggle: (String) -> Unit,
) {
    PremiumContentCard(title = section.title) {
            section.items.forEach { item ->
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                    ) {
                        Text(
                            text = item.question,
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.weight(1f),
                        )
                        IconButton(onClick = { onToggle(item.question) }) {
                            Icon(
                                imageVector = if (expandedQuestion == item.question) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                                contentDescription = if (expandedQuestion == item.question) {
                                    stringResource(R.string.support_help_collapse_answer)
                                } else {
                                    stringResource(R.string.support_help_expand_answer)
                                },
                            )
                        }
                    }
                    if (expandedQuestion == item.question) {
                        Text(
                            text = item.answer,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
    }
}

@Composable
private fun UserGuideSectionCard(
    section: UserGuideSectionData,
    expanded: Boolean,
    onToggle: () -> Unit,
) {
    PremiumContentCard {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = section.title,
                    style = MaterialTheme.typography.titleMedium,
                )
                IconButton(onClick = onToggle) {
                    Icon(
                        imageVector = if (expanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                        contentDescription = if (expanded) {
                            stringResource(R.string.support_guide_collapse_section)
                        } else {
                            stringResource(R.string.support_guide_expand_section)
                        },
                    )
                }
            }
            if (expanded) {
                section.items.forEach { item ->
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(
                            text = item.heading,
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.SemiBold,
                        )
                        Text(
                            text = item.body,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
    }
}

private fun launchSupportEmail(
    context: android.content.Context,
    subject: String,
) {
    val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
        data = Uri.parse("mailto:support@astromeric.app")
        putExtra(Intent.EXTRA_SUBJECT, subject)
        putExtra(Intent.EXTRA_TEXT, supportEmailBody(context))
    }
    if (emailIntent.resolveActivity(context.packageManager) != null) {
        context.startActivity(emailIntent)
    }
}

private fun supportEmailBody(context: android.content.Context): String = buildString {
    appendLine(context.getString(R.string.support_email_body_prompt))
    appendLine()
    appendLine(context.getString(R.string.support_email_body_screen_or_feature))
    appendLine(context.getString(R.string.support_email_body_expected_result))
    appendLine(context.getString(R.string.support_email_body_actual_result))
    appendLine(context.getString(R.string.support_email_body_steps_to_reproduce))
    appendLine()
    appendLine("---")
    appendLine(context.getString(R.string.support_email_body_diagnostics))
    appendLine(context.getString(R.string.support_email_body_version, BuildConfig.VERSION_NAME, BuildConfig.VERSION_CODE))
    appendLine(context.getString(R.string.support_email_body_android, Build.VERSION.RELEASE))
    appendLine(context.getString(R.string.support_email_body_device, Build.MANUFACTURER, Build.MODEL))
    appendLine()
    append(context.getString(R.string.support_email_body_privacy_note))
}

private data class HelpSectionData(
    val title: String,
    val items: List<HelpItemData>,
)

private data class HelpItemData(
    val question: String,
    val answer: String,
)

private data class UserGuideSectionData(
    val title: String,
    val items: List<UserGuideItemData>,
)

private data class UserGuideItemData(
    val heading: String,
    val body: String,
)

private fun helpSections(context: Context) = listOf(
    HelpSectionData(
        title = context.getString(R.string.support_help_section_account_profile_title),
        items = listOf(
            HelpItemData(
                question = context.getString(R.string.support_help_question_create_profile),
                answer = context.getString(R.string.support_help_answer_create_profile),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_multiple_profiles),
                answer = context.getString(R.string.support_help_answer_multiple_profiles),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_unknown_birth_time),
                answer = context.getString(R.string.support_help_answer_unknown_birth_time),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_edit_birth_details),
                answer = context.getString(R.string.support_help_answer_edit_birth_details),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_delete_data),
                answer = context.getString(R.string.support_help_answer_delete_data),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_hide_sensitive_details),
                answer = context.getString(R.string.support_help_answer_hide_sensitive_details),
            ),
        ),
    ),
    HelpSectionData(
        title = context.getString(R.string.support_help_section_readings_accuracy_title),
        items = listOf(
            HelpItemData(
                question = context.getString(R.string.support_help_question_same_reading),
                answer = context.getString(R.string.support_help_answer_same_reading),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_accuracy),
                answer = context.getString(R.string.support_help_answer_accuracy),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_chaldean),
                answer = context.getString(R.string.support_help_answer_chaldean),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_life_path_wrong),
                answer = context.getString(R.string.support_help_answer_life_path_wrong),
            ),
        ),
    ),
    HelpSectionData(
        title = context.getString(R.string.support_help_section_charts_astrology_title),
        items = listOf(
            HelpItemData(
                question = context.getString(R.string.support_help_question_same_day_different_profiles),
                answer = context.getString(R.string.support_help_answer_same_day_different_profiles),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_missing_house_lines),
                answer = context.getString(R.string.support_help_answer_missing_house_lines),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_house_system),
                answer = context.getString(R.string.support_help_answer_house_system),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_sun_sign_different),
                answer = context.getString(R.string.support_help_answer_sun_sign_different),
            ),
        ),
    ),
    HelpSectionData(
        title = context.getString(R.string.support_help_section_notifications_widgets_title),
        items = listOf(
            HelpItemData(
                question = context.getString(R.string.support_help_question_enable_daily_reminder),
                answer = context.getString(R.string.support_help_answer_enable_daily_reminder),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_widget_old_data),
                answer = context.getString(R.string.support_help_answer_widget_old_data),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_add_widget),
                answer = context.getString(R.string.support_help_answer_add_widget),
            ),
        ),
    ),
    HelpSectionData(
        title = context.getString(R.string.support_help_section_compatibility_friends_title),
        items = listOf(
            HelpItemData(
                question = context.getString(R.string.support_help_question_add_friend_compatibility),
                answer = context.getString(R.string.support_help_answer_add_friend_compatibility),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_compatibility_percentage),
                answer = context.getString(R.string.support_help_answer_compatibility_percentage),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_friend_data_disappeared),
                answer = context.getString(R.string.support_help_answer_friend_data_disappeared),
            ),
        ),
    ),
    HelpSectionData(
        title = context.getString(R.string.support_help_section_troubleshooting_title),
        items = listOf(
            HelpItemData(
                question = context.getString(R.string.support_help_question_unable_to_load),
                answer = context.getString(R.string.support_help_answer_unable_to_load),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_clear_cache),
                answer = context.getString(R.string.support_help_answer_clear_cache),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_report_crash),
                answer = context.getString(R.string.support_help_answer_report_crash),
            ),
            HelpItemData(
                question = context.getString(R.string.support_help_question_readings_not_updating),
                answer = context.getString(R.string.support_help_answer_readings_not_updating),
            ),
        ),
    ),
)

private fun filterFaqSections(context: Context, query: String): List<HelpSectionData> {
    if (query.isBlank()) {
        return helpSections(context)
    }
    val lowered = query.trim().lowercase()
    return helpSections(context).mapNotNull { section ->
        val filteredItems = section.items.filter { item ->
            item.question.lowercase().contains(lowered) || item.answer.lowercase().contains(lowered)
        }
        filteredItems.takeIf { it.isNotEmpty() }?.let { section.copy(items = it) }
    }
}

private fun userGuideSections(context: Context) = listOf(
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_getting_started_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_create_profile),
                body = context.getString(R.string.support_guide_body_create_profile),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_birth_time_matters),
                body = context.getString(R.string.support_guide_body_birth_time_matters),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_multi_profile_support),
                body = context.getString(R.string.support_guide_body_multi_profile_support),
            ),
        ),
    ),
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_home_daily_reading_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_daily_reading),
                body = context.getString(R.string.support_guide_body_daily_reading),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_morning_brief),
                body = context.getString(R.string.support_guide_body_morning_brief),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_personal_day_number),
                body = context.getString(R.string.support_guide_body_personal_day_number),
            ),
        ),
    ),
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_numerology_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_life_path_number),
                body = context.getString(R.string.support_guide_body_life_path_number),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_expression_soul_urge_personality),
                body = context.getString(R.string.support_guide_body_expression_soul_urge_personality),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_pythagorean_vs_chaldean),
                body = context.getString(R.string.support_guide_body_pythagorean_vs_chaldean),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_personal_year_month),
                body = context.getString(R.string.support_guide_body_personal_year_month),
            ),
        ),
    ),
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_birth_chart_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_reading_your_chart),
                body = context.getString(R.string.support_guide_body_reading_your_chart),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_planets_signs_houses_aspects),
                body = context.getString(R.string.support_guide_body_planets_signs_houses_aspects),
            ),
        ),
    ),
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_compatibility_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_synastry),
                body = context.getString(R.string.support_guide_body_synastry),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_cosmic_circle),
                body = context.getString(R.string.support_guide_body_cosmic_circle),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_score_means),
                body = context.getString(R.string.support_guide_body_score_means),
            ),
        ),
    ),
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_year_ahead_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_solar_return),
                body = context.getString(R.string.support_guide_body_solar_return),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_life_phase),
                body = context.getString(R.string.support_guide_body_life_phase),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_eclipses_monthly_forecast),
                body = context.getString(R.string.support_guide_body_eclipses_monthly_forecast),
            ),
        ),
    ),
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_tools_features_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_calculated_vs_interpretive),
                body = context.getString(R.string.support_guide_body_calculated_vs_interpretive),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_tarot_oracle_birthstone),
                body = context.getString(R.string.support_guide_body_tarot_oracle_birthstone),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_cosmic_habits_journal_widgets),
                body = context.getString(R.string.support_guide_body_cosmic_habits_journal_widgets),
            ),
        ),
    ),
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_notifications_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_daily_reading_reminder),
                body = context.getString(R.string.support_guide_body_daily_reading_reminder),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_notifications_morning_brief),
                body = context.getString(R.string.support_guide_body_notifications_morning_brief),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_disabling_notifications),
                body = context.getString(R.string.support_guide_body_disabling_notifications),
            ),
        ),
    ),
    UserGuideSectionData(
        title = context.getString(R.string.support_guide_section_tips_tricks_title),
        items = listOf(
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_pull_to_refresh),
                body = context.getString(R.string.support_guide_body_pull_to_refresh),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_long_press_profiles),
                body = context.getString(R.string.support_guide_body_long_press_profiles),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_context_aware_ai),
                body = context.getString(R.string.support_guide_body_context_aware_ai),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_hide_sensitive_details),
                body = context.getString(R.string.support_guide_body_hide_sensitive_details),
            ),
            UserGuideItemData(
                heading = context.getString(R.string.support_guide_heading_chaldean_toggle),
                body = context.getString(R.string.support_guide_body_chaldean_toggle),
            ),
        ),
    ),
)